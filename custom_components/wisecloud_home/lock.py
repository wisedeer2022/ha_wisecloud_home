import logging

from homeassistant.components.lock import LockEntity, LockEntityFeature, LockState
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
        lockEntity = WiseCloudLock(device['deviceIotId'], device_info)
        entities.append(lockEntity)
    hass.data[DOMAIN]["lock_entities"] = entities
    # 添加所有实体
    async_add_entities(entities)

class WiseCloudLock(LockEntity):
    def __init__(self, device_id, device_info):
        self._device_id = device_id
        self._attr_device_info = device_info
        self._is_locked = None
        self._attr_name = "门锁状态"
        self._attr_unique_id = f"{device_id}-lock"

    @property
    def name(self):
        return self._attr_name

    @property
    def unique_id(self):
        return self._attr_unique_id

    @property
    def state(self):
        if self._is_locked is None:
            return None
        return LockState.LOCKED if self._is_locked else LockState.UNLOCKED

    @property
    def is_locked(self):
        return self._is_locked

    async def async_lock(self, **kwargs):
        _LOGGER.warning("This device does not support remote locking.")

    async def async_unlock(self, **kwargs):
        _LOGGER.warning("This device does not support remote unlocking.")


    async def sync_state(self, state):
        self._is_locked = state
        self.async_write_ha_state()
