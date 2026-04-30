from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorEntityDescription, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfElectricPotential, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import WatercoolerDataUpdateCoordinator


def _mode_text(data: dict) -> str:
    mode = data.get("mode")
    return "自动模式" if mode == "auto" else "手动模式"


def _device_text(data: dict) -> str:
    if not data.get("connected"):
        return "未连接"
    return data.get("device_name") or "已连接"


def _nested(data: dict, *keys, default=None):
    cur: Any = data
    for key in keys:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(key)
    return default if cur is None else cur


@dataclass(frozen=True, kw_only=True)
class WatercoolerSensorDescription(SensorEntityDescription):
    value_fn: Callable[[dict], Any]
    attr_fn: Callable[[dict], dict[str, Any]] | None = None


SENSORS: tuple[WatercoolerSensorDescription, ...] = (
    WatercoolerSensorDescription(
        key="device",
        name="水冷设备",
        icon="mdi:bluetooth",
        value_fn=_device_text,
        attr_fn=lambda d: {
            "connected": d.get("connected"),
            "device_name": d.get("device_name"),
            "connection_uptime": _nested(d, "connection_uptime", "text"),
        },
    ),
    WatercoolerSensorDescription(
        key="mode",
        name="水冷模式",
        icon="mdi:tune-variant",
        value_fn=_mode_text,
        attr_fn=lambda d: d.get("auto", {}),
    ),
    WatercoolerSensorDescription(
        key="fan_percent",
        name="风扇功率",
        icon="mdi:fan",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: _nested(d, "fan", "percent"),
        attr_fn=lambda d: d.get("fan", {}),
    ),
    WatercoolerSensorDescription(
        key="pump_voltage",
        name="水泵功率",
        icon="mdi:pump",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: _nested(d, "pump", "voltage"),
        attr_fn=lambda d: d.get("pump", {}),
    ),
    WatercoolerSensorDescription(
        key="rgb_effect",
        name="RGB 灯效",
        icon="mdi:led-strip-variant",
        value_fn=lambda d: _nested(d, "rgb", "text", default="未知"),
        attr_fn=lambda d: d.get("rgb", {}),
    ),
    WatercoolerSensorDescription(
        key="cpu_temperature",
        name="CPU 温度",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: _nested(d, "temperature", "cpu_c"),
    ),
    WatercoolerSensorDescription(
        key="gpu_temperature",
        name="显卡温度",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: _nested(d, "temperature", "gpu_c"),
    ),
    WatercoolerSensorDescription(
        key="uptime",
        name="已运行时间",
        icon="mdi:timer-outline",
        value_fn=lambda d: _nested(d, "uptime", "text", default="0 秒"),
        attr_fn=lambda d: {
            "seconds": _nested(d, "uptime", "seconds"),
            "connection_seconds": _nested(d, "connection_uptime", "seconds"),
            "connection_text": _nested(d, "connection_uptime", "text"),
        },
    ),
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator: WatercoolerDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(WatercoolerSensor(coordinator, entry, description) for description in SENSORS)


class WatercoolerSensor(CoordinatorEntity[WatercoolerDataUpdateCoordinator], SensorEntity):
    entity_description: WatercoolerSensorDescription

    def __init__(self, coordinator: WatercoolerDataUpdateCoordinator, entry: ConfigEntry, description: WatercoolerSensorDescription) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_has_entity_name = True
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "水冷管理器",
            "manufacturer": "watercooler-manager",
        }

    @property
    def native_value(self):
        return self.entity_description.value_fn(self.coordinator.data or {})

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        if self.entity_description.attr_fn is None:
            return None
        return self.entity_description.attr_fn(self.coordinator.data or {})
