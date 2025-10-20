from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.device_registry import DeviceInfo
from .const import DOMAIN


async def async_setup_entry(hass, config_entry, async_add_entities):
    devices = hass.data[DOMAIN][config_entry.entry_id]["devices"]

    entities = []
    for device in devices:
        device_info = DeviceInfo(
            identifiers={(DOMAIN, device['deviceIotId'])},
        )
        lock_log_entity = WiseCloudSensor(device['deviceIotId'], "lock_log", "门锁日志", device_info)
        entities.append(lock_log_entity)
    hass.data[DOMAIN]["sensor_entities"] = entities
    # 添加所有实体
    async_add_entities(entities)

class WiseCloudSensor(SensorEntity):
    def __init__(self, device_id, prop_id, name, device_info):

        self.device_id = device_id
        self.prop_id = prop_id
        self._attr_name = name  # 实体显示名称
        self._attr_unique_id = f"{device_id}-{prop_id}"
        self._attr_device_info = device_info

    @property
    def device_info(self):
        return self._attr_device_info

    @property
    def should_poll(self) -> bool:
        return False

    @property
    def state(self) -> str:
        return self._attr_state  # 用自定义变量存储消息

    async def sync_state(self, message):
        print(message)
        self._attr_state = message
        self.async_write_ha_state()
