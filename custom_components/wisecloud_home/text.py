import asyncio

from homeassistant.components.text import TextEntity
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    devices = hass.data[DOMAIN][entry.entry_id]["devices"]
    client = hass.data[DOMAIN][entry.entry_id]["client"]

    entities = []
    for device in devices:
        device_info = DeviceInfo(
            identifiers={(DOMAIN, device['deviceIotId'])},
        )
        strings = device["strings"]
        for string in strings:
            define = string["define"]
            textEntity = WiseCloudText(client, device["deviceIotId"], string["id"], string["name"],
                                           define["min"], define["max"], device_info)
            entities.append(textEntity)
    hass.data[DOMAIN]["text_entities"] = entities
    # 添加所有实体
    async_add_entities(entities)


class WiseCloudText(TextEntity):
    """Representation of an Example Text entity."""

    def __init__(self, client, device_id: str, prop_id, name, min, max, device_info):
        self._client = client
        self._device_id = device_id
        self._prop_id = prop_id
        self._attr_native_value = min
        self._min_value = int(min)
        self._max_value = int(max)
        self._attr_unique_id = f"{device_id}-{prop_id}"
        self._attr_name = name
        self._attr_device_info = device_info


    async def sync_state(self, value):
        self._attr_native_value = value
        self.async_write_ha_state()
