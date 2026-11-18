"""Switch platform for the Huawei SUN2000 integration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.const import EntityCategory

from .entity import HuaweiSunEntity

if TYPE_CHECKING:
    from collections.abc import Callable

    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import HuaweiSunCoordinator
    from .data import HuaweiSunConfigEntry
    from .vendor.huawei_modbus import HuaweiSun2000


@dataclass(frozen=True, kw_only=True)
class HuaweiSwitchEntityDescription(SwitchEntityDescription):
    """Describe an on/off setting backed by one register."""

    component: str
    """Device attribute that holds the block this setting belongs to."""
    report_name: str
    """Name of the block in the coordinator's update report."""
    field: str
    """Field name inside that block."""
    value_fn: Callable[[HuaweiSun2000], bool | None]


SWITCHES: tuple[HuaweiSwitchEntityDescription, ...] = (
    HuaweiSwitchEntityDescription(
        key="battery_charge_from_grid",
        translation_key="battery_charge_from_grid",
        component="battery_settings",
        report_name="battery_settings",
        field="charge_from_grid",
        entity_category=EntityCategory.CONFIG,
        icon="mdi:transmission-tower-import",
        value_fn=lambda device: (
            device.battery_settings.charge_from_grid
            if device.battery_settings
            else None
        ),
    ),
)


async def async_setup_entry(
    _hass: HomeAssistant,
    entry: HuaweiSunConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the switch entities of one inverter."""
    coordinator = entry.runtime_data.coordinator
    async_add_entities(
        HuaweiSunSwitch(coordinator, description)
        for description in SWITCHES
        if getattr(coordinator.device, description.component, None) is not None
    )


class HuaweiSunSwitch(HuaweiSunEntity, SwitchEntity):
    """An on/off setting read from and written to one register."""

    entity_description: HuaweiSwitchEntityDescription

    def __init__(
        self,
        coordinator: HuaweiSunCoordinator,
        description: HuaweiSwitchEntityDescription,
    ) -> None:
        """Initialize the setting."""
        super().__init__(coordinator, description.component)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{description.key}"

    @property
    def is_on(self) -> bool | None:
        """Return the current setting."""
        return self.entity_description.value_fn(self.coordinator.device)

    async def async_turn_on(self, **_kwargs: object) -> None:
        """Enable the setting."""
        await self.coordinator.async_write(
            self.entity_description.component,
            self.entity_description.field,
            value=True,
        )

    async def async_turn_off(self, **_kwargs: object) -> None:
        """Disable the setting."""
        await self.coordinator.async_write(
            self.entity_description.component,
            self.entity_description.field,
            value=False,
        )
