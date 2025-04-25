from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.helpers.device_registry import DeviceInfo
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    devices = hass.data[DOMAIN][entry.entry_id]["devices"]
    entities = []
    for device in devices:
        device_info = DeviceInfo(
            identifiers={(DOMAIN, device['deviceIotId'])},
        )
        unlock_method_entity = WiseCloudSensor(device['deviceIotId'], "unlock_method_sensor", "开锁方式",
                                           device_info)
        entities.append(unlock_method_entity)
    hass.data[DOMAIN]["sensor_entities"] = entities
    # 添加所有实体
    async_add_entities(entities)


class WiseCloudSensor(SensorEntity):
    """Representation of an Example Sensor entity."""

    def __init__(self, device_id: str, prop_id, name, device_info):
        """Initialize the sensor."""
        self._attr_unique_id = f"{device_id}-{prop_id}"
        self._attr_name = name
        self._attr_native_value = None
        self.unlock_method_mapping = {
            1: "蓝牙",
            2: "指纹",
            3: "密码",
            4: "NFC",
            5: "人脸",
            7: "掌静脉",
            8: "机械钥匙",
            9: "一次性密码",
            10: "周期性密码",
            13: "双重验证",
            15: "手动",
            16: "自动",
            17: "门内按键",
            100: "上锁"
        }
        self._attr_options = [str(i) for i in list(self.unlock_method_mapping.values())]
        self._attr_device_info = device_info
        self._attr_device_class = SensorDeviceClass.ENUM



    async def sync_state(self, value):
        self._attr_native_value = self.unlock_method_mapping[value]
        self.async_write_ha_state()
