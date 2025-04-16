import json
import logging

from homeassistant.components.event import EventEntity
from homeassistant.helpers.device_registry import DeviceInfo
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    devices = hass.data[DOMAIN][config_entry.entry_id]["devices"]

    entities = []
    for device in devices:
        device_info = DeviceInfo(
            identifiers={(DOMAIN, device['deviceIotId'])},
        )
        events = device["events"]
        print(json.dumps(events))
        for event in events:
            mapping = event["mapping"]
            event_entity = WiseCloudEvent(hass,device['deviceIotId'], event["id"], event["name"], mapping, device_info)
            entities.append(event_entity)

        pseudo_mapping = {
            "inside_unlock": "门内开锁",
            "outside_unlock": "门外开锁",
            "unknown_unlock": "开锁(内外未知)",
            "locked":"上锁"
        }
        lock_event_entity = WiseCloudEvent(hass, device['deviceIotId'], "pseudo_lock_event", "门锁事件", pseudo_mapping, device_info)
        entities.append(lock_event_entity)

    hass.data[DOMAIN]["event_entities"] = entities
    # 添加所有实体
    async_add_entities(entities)



class WiseCloudEvent(EventEntity):


    """表示一个定期触发事件的实体"""

    def __init__(self, hass, device_id, prop_id, name, mapping, device_info):
        self._hass = hass
        self._attr_unique_id = f"{device_id}-{prop_id}"
        self._attr_name = name
        self._mapping = mapping
        self._attr_event_types = list(mapping.values())
        self._device_info = device_info


    @property
    def device_info(self):
        return self._device_info


    @property
    def should_poll(self):
        """不需要轮询"""
        return False



    async def trigger(self, event_type: str, message):
        """触发自定义事件"""
        event_data = {
            'entity_id': self.entity_id,
            'message': message,
        }
        self._trigger_event(self._mapping[event_type], event_data)
        self.async_write_ha_state()
        _LOGGER.info(f"Fired event: {self._mapping[event_type]} with data: {event_data}")
