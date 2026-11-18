"""Binary sensor platform for the Huawei SUN2000 integration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)

from .entity import HuaweiSunEntity
from .vendor.huawei_modbus.values import STORAGE_CONNECTED_VALUES

if TYPE_CHECKING:
    from collections.abc import Callable

    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import HuaweiSunCoordinator
    from .data import HuaweiSunConfigEntry
    from .vendor.huawei_modbus import HuaweiSun2000

#: Battery running state that means the unit reported a fault (register 37000).
STORAGE_FAULT = 3


@dataclass(frozen=True, kw_only=True)
class HuaweiBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Describe a two-state reading backed by the device object."""

    component: str
    """Device attribute that must exist for this entity to be created."""
    report_name: str
    """Name of the block in the coordinator's update report."""
    value_fn: Callable[[HuaweiSun2000], bool | None]


BINARY_SENSORS: tuple[HuaweiBinarySensorEntityDescription, ...] = (
    HuaweiBinarySensorEntityDescription(
        key="problem",
        translation_key="problem",
        component="telemetry",
        report_name="telemetry",
        device_class=BinarySensorDeviceClass.PROBLEM,
        value_fn=lambda device: (
            bool(
                device.telemetry.alarm_1
                or device.telemetry.alarm_2
                or device.telemetry.alarm_3
            )
            or (
                device.battery is not None
                and (
                    device.battery.running_status == STORAGE_FAULT
                    or bool(device.battery.fault_id)
                )
            )
        ),
    ),
    HuaweiBinarySensorEntityDescription(
        key="battery_connected",
        translation_key="battery_connected",
        component="battery_status",
        report_name="battery_status",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        value_fn=lambda device: (
            device.battery_status.connect_status in STORAGE_CONNECTED_VALUES
            if device.battery_status is not None
            else None
        ),
    ),
)


async def async_setup_entry(
    _hass: HomeAssistant,
    entry: HuaweiSunConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the binary sensors of one inverter."""
    coordinator = entry.runtime_data.coordinator
    async_add_entities(
        HuaweiSunBinarySensor(coordinator, description)
        for description in BINARY_SENSORS
        if getattr(coordinator.device, description.component, None) is not None
    )


class HuaweiSunBinarySensor(HuaweiSunEntity, BinarySensorEntity):
    """A two-state reading taken from the device object."""

    entity_description: HuaweiBinarySensorEntityDescription

    def __init__(
        self,
        coordinator: HuaweiSunCoordinator,
        description: HuaweiBinarySensorEntityDescription,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator, description.component)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{description.key}"

    @property
    def is_on(self) -> bool | None:
        """Return the current state."""
        return self.entity_description.value_fn(self.coordinator.device)
