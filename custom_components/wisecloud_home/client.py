import json

from .api import WiseCloudAPI


class WiseCloudClient:
    def __init__(self, api: WiseCloudAPI):
        self._api = api


    async def get_devices(self):
        return await self._api.request("GET","/open/api/devices")

    async def get_models(self, product_id: str):
        modelStr = await self._api.request("GET","/open/api/devices/models/" + product_id)
        return json.loads(modelStr)

    async def get_all_status(self, device_iot_id: str):
        statusStr = await self._api.request("GET","/open/api/devices/status/" + device_iot_id)
        stauts = json.loads(statusStr)

        # print(f"get_all_status:{stauts}")

        return stauts

    async def device_control(self, device_iot_id: str, control_data: dict, notify_device: int = 0):
        param = {
            "deviceNotifyEnable": notify_device,
            "data": json.dumps(control_data),
        }
        await self._api.request("PUT","/open/api/devices/control/" + device_iot_id, data=param)

