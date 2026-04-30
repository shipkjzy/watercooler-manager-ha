from __future__ import annotations

from typing import Any

from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import WatercoolerDataUpdateCoordinator


def _nested(data: dict, *keys, default=None):
    cur: Any = data
    for key in keys:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(key)
    return default if cur is None else cur


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator: WatercoolerDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([WatercoolerConnectionBinarySensor(coordinator, entry)])


class WatercoolerConnectionBinarySensor(CoordinatorEntity[WatercoolerDataUpdateCoordinator], BinarySensorEntity):
    def __init__(self, coordinator: WatercoolerDataUpdateCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_connection_status"
        self._attr_name = "连接状态"
        self._attr_has_entity_name = True
        self._attr_device_class = BinarySensorDeviceClass.CONNECTIVITY
        self._attr_icon = "mdi:bluetooth-connect"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "水冷管理器",
            "manufacturer": "watercooler-manager",
        }

    @property
    def is_on(self) -> bool:
        return bool((self.coordinator.data or {}).get("connected"))

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        data = self.coordinator.data or {}
        return {
            "connected": bool(data.get("connected")),
            "device_name": data.get("device_name"),
            "connection_uptime_seconds": _nested(data, "connection_uptime", "seconds"),
            "connection_uptime_text": _nested(data, "connection_uptime", "text"),
            "api_timestamp": data.get("timestamp"),
        }
