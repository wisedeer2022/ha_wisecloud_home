from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import aiohttp_client, config_entry_oauth2_flow
from homeassistant.helpers.device_registry import DeviceInfo, async_get
from . import api
from .application_credentials import async_get_auth_implementation
from .client import WiseCloudClient
from .const import DOMAIN
from .spec_parser import parse
from .ws import WSClient

PLATFORMS: list[Platform] = [
    Platform.SELECT,
    Platform.EVENT,
    Platform.LOCK,
    Platform.TEXT,
    Platform.SWITCH,
    Platform.NUMBER,
]

type New_NameConfigEntry = ConfigEntry[api.WiseCloudAPI]


async def async_setup_entry(hass: HomeAssistant, entry: New_NameConfigEntry) -> bool:
    implementation = await async_get_auth_implementation(hass, DOMAIN)
    session = config_entry_oauth2_flow.OAuth2Session(hass, entry, implementation)
    # If using an aiohttp-based API lib
    auth = api.WiseCloudAPI(
        aiohttp_client.async_get_clientsession(hass), session
    )

    client = WiseCloudClient(auth)
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "client": client
    }

    devices = await client.get_devices()
    hass.data[DOMAIN][entry.entry_id]["devices"] = devices

    for device in devices:
        spec = await client.get_models(device["iotProductId"])
        switchs, strings, numbers, selects, sensors, events = await parse(spec)

        print(f"{switchs}, {strings}, {numbers}, {selects}, {sensors}, {events}")

        device["switchs"] = switchs
        device["strings"] = strings
        device["numbers"] = numbers
        device["selects"] = selects
        device["sensors"] = sensors
        device["events"] = events

        # 获取设备信息
        device_all_status = await client.get_all_status(device["deviceIotId"])
        device_information = device_all_status["device_information"]["Value"]
        # 提取设备信息并构建 DeviceInfo
        device_info = DeviceInfo(
            identifiers={(DOMAIN, device['deviceIotId'])},
            name=device.get('noteName', device['noteName']),
            manufacturer=device.get('manufacturer', device_information["manufacturer"]),
            model=device.get('model', device_information["model"]),
            sw_version=device.get('sw_version', device_information["main_version"]),
        )
        # 注册设备
        device_registry = async_get(hass)
        device_registry.async_get_or_create(
            config_entry_id=entry.entry_id,
            **device_info
        )

    # 建立ws连接
    wsClient = WSClient(hass, auth)
    hass.async_create_task(wsClient.connect_ws())
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True



async def async_unload_entry(hass: HomeAssistant, entry: New_NameConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
