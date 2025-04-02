from homeassistant.components.number import NumberEntity
from homeassistant.helpers.device_registry import DeviceInfo
from .const import DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):
    devices = hass.data[DOMAIN][entry.entry_id]["devices"]
    client = hass.data[DOMAIN][entry.entry_id]["client"]

    entities = []
    for device in devices:
        device_info = DeviceInfo(
            identifiers={(DOMAIN, device['deviceIotId'])},
        )
        numbers = device["numbers"]
        for number in numbers:
            define = number["define"]
            numberEntity = WiseCloudNumber(client, device["deviceIotId"], number["id"], number["name"],
                                           define["min"], define["max"], device_info)
            entities.append(numberEntity)
    hass.data[DOMAIN]["number_entities"] = entities
    # 添加所有实体
    async_add_entities(entities)


class WiseCloudNumber(NumberEntity):
    def __init__(self, client, device_id: str, prop_id, name, min, max, device_info):
        self._client = client
        self._device_id = device_id
        self._prop_id = prop_id
        self._attr_native_value = min
        self._attr_native_min_value = int(min)
        self._attr_native_max_value = int(max)
        self._attr_unique_id = f"{device_id}-{prop_id}"
        self._attr_name = name
        self._attr_device_info = device_info


    async def async_set_native_value(self, value: float) -> None:
        """Set new value."""
        if self._attr_native_min_value <= value <= self._attr_native_max_value:
            self._attr_native_value = value
            control_data = {
                self._prop_id: self._attr_native_value
            }
            await self._client.device_control(self._device_id, control_data, 1)
        self.async_write_ha_state()



    async def sync_state(self, state):
        if self._attr_native_min_value <= state <= self._attr_native_max_value:
            self._attr_native_value = state
            self.async_write_ha_state()