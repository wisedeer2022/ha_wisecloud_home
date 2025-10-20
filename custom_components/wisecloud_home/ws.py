import asyncio
import json
import ssl

import websockets

from homeassistant.helpers.entity_registry import async_get as async_get_entity_registry
from .api import WiseCloudAPI
from .const import WS_BASE_URL, DOMAIN


class WSClient:

    def __init__(self, hass, api: WiseCloudAPI):
        self.hass = hass
        self.api = api

    async def connect_ws(self):
        max_retries = 5  # 最大重试次数
        retry_delay = 5  # 每次重试的延迟时间（秒）
        retries = 0

        while retries < max_retries:
            access_token = await self.api.async_get_access_token()
            try:
                def load_certs():
                    context = ssl.create_default_context()
                    context.load_default_certs()
                    return context

                # 在执行器中运行加载证书的操作
                ssl_context = await self.hass.async_add_executor_job(load_certs)
                async with websockets.connect(f"{WS_BASE_URL}?token={access_token}", ssl=ssl_context) as websocket:
                    print('connected')
                    # 启动心跳任务
                    heartbeat_task = asyncio.create_task(self.send_heartbeat(websocket))
                    # 首次获取所有状态
                    await websocket.send("pull_all_property")
                    while True:
                        message = await websocket.recv()
                        await self.handle_ws_message(message)
            except websockets.exceptions.ConnectionClosedOK:
                heartbeat_task.cancel()
                print("WebSocket connection closed normally.")
            except Exception as e:
                websocket.close()
                print(f"WebSocket error: {e}")
                retries += 1
                if retries < max_retries:
                    print(f"Retrying in {retry_delay} seconds... (Attempt {retries + 1} of {max_retries})")
                    await asyncio.sleep(retry_delay)
                else:
                    print("Max retries reached. Giving up.")



    async def send_heartbeat(self, websocket):
        while True:
            try:
                await asyncio.sleep(120)  # 2 分钟 = 120 秒
                await websocket.send("ping")
            except websockets.exceptions.ConnectionClosed:
                print("WebSocket 连接已关闭，心跳机制停止。")
                break

    async def handle_ws_message(self, message):
        try:
            msgJson = json.loads(message)
            print(msgJson)
            if msgJson["code"] == 200 :
                dataJson = msgJson["data"]
                deviceIotId = dataJson["deviceIotId"]
                contentJson = json.loads(dataJson["content"])
                # 获取实体注册表
                entity_registry = async_get_entity_registry(self.hass)
                if dataJson["msgType"] == "PROPERTY":
                    for key, value in contentJson.items():
                        # 根据 unique_id 获取实体 ID
                        entity_id = entity_registry.async_get_entity_id('select', DOMAIN, f"{deviceIotId}-{key}")
                        if entity_id:
                            select_entities = self.hass.data[DOMAIN]["select_entities"]
                            for select_entity in select_entities:
                                if select_entity.entity_id == entity_id:
                                    await select_entity.sync_state(str(value["Value"]))
                                    continue
                        entity_id = entity_registry.async_get_entity_id('switch', DOMAIN, f"{deviceIotId}-{key}")
                        if entity_id:
                            switch_entities = self.hass.data[DOMAIN]["switch_entities"]
                            for switch_entity in switch_entities:
                                if switch_entity.entity_id == entity_id:
                                    await switch_entity.sync_state(value["Value"])
                                    continue
                        entity_id = entity_registry.async_get_entity_id('number', DOMAIN, f"{deviceIotId}-{key}")
                        if entity_id:
                            number_entities = self.hass.data[DOMAIN]["number_entities"]
                            for number_entity in number_entities:
                                if number_entity.entity_id == entity_id:
                                    await number_entity.sync_state(value["Value"])
                                    continue
                        entity_id = entity_registry.async_get_entity_id('text', DOMAIN, f"{deviceIotId}-{key}")
                        if entity_id:
                            text_entities = self.hass.data[DOMAIN]["text_entities"]
                            for text_entity in text_entities:
                                if text_entity.entity_id == entity_id:
                                    await text_entity.sync_state(value["Value"])
                                    continue
                elif dataJson["msgType"] == "EVENT":
                    message = contentJson["event_title"]
                    ext = contentJson["ext"]
                    if not ext:
                        return
                    iot_event_id = ext['iot_event_id']
                    extra = json.loads(ext["extra"])
                    event_type = self.parse_event_type(iot_event_id, extra)
                    # 根据 unique_id 获取实体 ID
                    entity_id = entity_registry.async_get_entity_id('event', DOMAIN, f"{deviceIotId}-{iot_event_id}")
                    if entity_id:
                        event_entities = self.hass.data[DOMAIN]["event_entities"]
                        for event_entity in event_entities:
                            if event_entity.entity_id == entity_id:
                                await event_entity.trigger(str(event_type), message)
                                break

                    if iot_event_id == 'lock_event':
                        lock_entity = self.hass.data[DOMAIN]["lock_entities"][0]
                        await lock_entity.sync_state(True if event_type != 2 else False)

                        # 处理虚构的门锁事件
                        entity_id = entity_registry.async_get_entity_id('event', DOMAIN,
                                                                        f"{deviceIotId}-pseudo_lock_event")
                        if entity_id:
                            event_entities = self.hass.data[DOMAIN]["event_entities"]
                            for event_entity in event_entities:
                                if event_entity.entity_id == entity_id:
                                    event_type = self.parse_pseudo_lock_event_type(extra)
                                    if event_type is not None:
                                        await event_entity.trigger(str(event_type), message)
                                    break

                        # 处理虚构的门锁日志
                        entity_id = entity_registry.async_get_entity_id('sensor', DOMAIN,
                                                                        f"{deviceIotId}-lock_log")
                        if entity_id:
                            sensor_entities = self.hass.data[DOMAIN]["sensor_entities"]
                            for sensor_entity in sensor_entities:
                                if sensor_entity.entity_id == entity_id:
                                    await sensor_entity.sync_state(message)
                                    break



        except json.JSONDecodeError:
            print(f"Failed to decode message: {message}")

    def parse_event_type(self, iot_event_id, extra) -> str:
        if iot_event_id == "lock_event":
            event_type = extra["lock_action"]
        elif iot_event_id == "camera_event":
            event_type = extra["event_type"]
        elif iot_event_id == "lock_exception":
            event_type = extra["abnormal_condition"]
        elif iot_event_id == "power_supply_event":
            event_type = extra["power_supply_mode"]
        return event_type


    def parse_pseudo_lock_event_type(self, extra):
        print(extra)
        lock_action = extra['lock_action']
        if lock_action == 1:
            return "locked"
        elif lock_action == 2:
            operation_position = extra['operation_position']
            if operation_position == 1:
                return "inside_unlock"
            elif operation_position == 2:
                return "outside_unlock"
            else:
                return "unknown_unlock"
        return None
