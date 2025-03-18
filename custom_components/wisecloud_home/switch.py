from homeassistant.components.switch import SwitchEntity
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
        switchs = device["switchs"]
        for switch in switchs:
            define = switch["define"]
            switchEntity = WiseCloudSwitch(client, device["deviceIotId"], switch["id"], switch["name"], define["mapping"], device_info)
            entities.append(switchEntity)

    hass.data[DOMAIN]["switch_entities"] = entities
    # 添加所有实体
    async_add_entities(entities)



class WiseCloudSwitch(SwitchEntity):
    def __init__(self, client, device_id: str, prop_id, name, mapping, device_info):
        self._client = client
        self._device_id = device_id
        self._prop_id = prop_id
        self._mapping = mapping
        self._attr_unique_id = f"{device_id}-{prop_id}"
        self._attr_name = name
        self._attr_device_info = device_info

    async def async_turn_on(self, **kwargs):
        """Turn the switch on."""
        self._attr_is_on = True
        control_data = {
            self._prop_id: 1 if self._attr_is_on else 0
        }
        await self._client.device_control(self._device_id, control_data, 1)
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        """Turn the switch off."""
        self._attr_is_on = False
        control_data = {
            self._prop_id: 1 if self._attr_is_on else 0
        }
        await self._client.device_control(self._device_id, control_data, 1)
        self.async_write_ha_state()

    async def sync_state(self, state):
        self._attr_is_on = (state == 1)
        self.async_write_ha_state()