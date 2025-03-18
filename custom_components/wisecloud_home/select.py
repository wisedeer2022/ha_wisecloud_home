from propcache import cached_property

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.helpers.device_registry import DeviceInfo
from .client import WiseCloudClient
from .const import DOMAIN


async def async_setup_entry(hass, config_entry, async_add_entities):
    devices = hass.data[DOMAIN][config_entry.entry_id]["devices"]
    client = hass.data[DOMAIN][config_entry.entry_id]["client"]

    entities = []
    for device in devices:
        device_info = DeviceInfo(
            identifiers={(DOMAIN, device['deviceIotId'])},
        )
        selects = device["selects"]
        for select in selects:
            define = select["define"]
            selectEntity = WiseCloudSelect(client, device["deviceIotId"], select["id"], select["name"], define["mapping"], device_info)
            entities.append(selectEntity)
    hass.data[DOMAIN]["select_entities"] = entities
    # 添加所有实体
    async_add_entities(entities)

class WiseCloudSelect(SelectEntity):
    def __init__(self, client, device_id, prop_id, name, mapping, device_info):
        self.client: WiseCloudClient = client
        self.device_id = device_id
        self.prop_id = prop_id
        self._attr_unique_id = f"{device_id}-{prop_id}"
        # 定义 SelectEntity 实体的描述信息
        self.entity_description = SelectEntityDescription(
            key=self._attr_unique_id,
            name=name,
        )
        self._mapping = mapping
        self._attr_options = [str(i) for i in list(mapping.values())]
        # 初始选中项
        self._attr_current_option = self._attr_options[0]
        self._attr_device_info = device_info


    async def sync_state(self, option):
        self._attr_current_option = self.find_v(option)
        self.async_write_ha_state()

    async def async_select_option(self, option: str) -> None:
        """处理用户选择选项的操作"""
        self._attr_current_option = self.find_k(option)
        control_data = {
            self.prop_id: self._attr_current_option
        }
        await self.client.device_control(self.device_id, control_data,1)
        # 这里可以添加将选择结果发送到数据源的逻辑
        # 例如，通过 API 请求更新数据源中的选中项
        self.async_write_ha_state()

    def find_v(self, k):
        return self._mapping[k]


    def find_k(self, v):
        for key, val in self._mapping.items():
            if val == v:
                return key
        return None
