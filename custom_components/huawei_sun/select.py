"""Select platform for the Huawei SUN2000 integration."""

from dataclasses import dataclass
from typing import TYPE_CHECKING

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.const import EntityCategory

from .entity import HuaweiSunEntity
from .vendor.huawei_modbus.values import (
    FORCIBLE_CHARGE_DISCHARGE,
    FORCIBLE_TARGET_MODE,
    STORAGE_WORKING_MODE,
)

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping

    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import HuaweiSunCoordinator
    from .data import HuaweiSunConfigEntry
    from .vendor.huawei_modbus import HuaweiSun2000


@dataclass(frozen=True, kw_only=True)
class HuaweiSelectEntityDescription(SelectEntityDescription):
    """Describe a named setting backed by one register."""

    component: str
    """Device attribute that holds the block this setting belongs to."""
    report_name: str
    """Name of the block in the coordinator's update report."""
    field: str
    """Field name inside that block."""
    value_map: Mapping[int, str]
    """Register value to the option shown in Home Assistant."""
    value_fn: Callable[[HuaweiSun2000], int | None]

    def __post_init__(self) -> None:
        """Expose the labels as the selectable options."""
        object.__setattr__(self, "options", list(self.value_map.values()))

    @property
    def option_values(self) -> dict[str, int]:
        """Map an option label back to the value written to the register."""
        return {label: value for value, label in self.value_map.items()}


SELECTS: tuple[HuaweiSelectEntityDescription, ...] = (
    HuaweiSelectEntityDescription(
        key="battery_working_mode",
        translation_key="battery_working_mode",
        component="battery_settings",
        report_name="battery_settings",
        field="working_mode",
        value_map=STORAGE_WORKING_MODE,
        entity_category=EntityCategory.CONFIG,
        icon="mdi:battery-sync",
        value_fn=lambda device: (
            device.battery_settings.working_mode if device.battery_settings else None
        ),
    ),
    HuaweiSelectEntityDescription(
        key="battery_forcible_charge_discharge",
        translation_key="battery_forcible_charge_discharge",
        component="battery_settings",
        report_name="battery_settings",
        field="forcible_charge_discharge",
        value_map=FORCIBLE_CHARGE_DISCHARGE,
        entity_category=EntityCategory.CONFIG,
        icon="mdi:battery-charging",
        value_fn=lambda device: (
            device.battery_settings.forcible_charge_discharge
            if device.battery_settings
            else None
        ),
    ),
    HuaweiSelectEntityDescription(
        key="battery_forcible_setting_mode",
        translation_key="battery_forcible_setting_mode",
        component="battery_forced",
        report_name="battery_forced",
        field="forcible_setting_mode",
        value_map=FORCIBLE_TARGET_MODE,
        entity_category=EntityCategory.CONFIG,
        icon="mdi:battery-clock",
        value_fn=lambda device: (
            device.battery_forced.forcible_setting_mode
            if device.battery_forced
            else None
        ),
    ),
)


async def async_setup_entry(
    _hass: HomeAssistant,
    entry: HuaweiSunConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the select entities of one inverter."""
    coordinator = entry.runtime_data.coordinator
    async_add_entities(
        HuaweiSunSelect(coordinator, description)
        for description in SELECTS
        if getattr(coordinator.device, description.component, None) is not None
    )


class HuaweiSunSelect(HuaweiSunEntity, SelectEntity):
    """A named setting read from and written to one register."""

    entity_description: HuaweiSelectEntityDescription

    def __init__(
        self,
        coordinator: HuaweiSunCoordinator,
        description: HuaweiSelectEntityDescription,
    ) -> None:
        """Initialize the setting."""
        super().__init__(coordinator, description.component)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{description.key}"

    @property
    def current_option(self) -> str | None:
        """Return the label of the value the register holds."""
        value = self.entity_description.value_fn(self.coordinator.device)
        if value is None:
            return None
        return self.entity_description.value_map.get(value)

    async def async_select_option(self, option: str) -> None:
        """Write the value behind the chosen label."""
        await self.coordinator.async_write(
            self.entity_description.component,
            self.entity_description.field,
            self.entity_description.option_values[option],
        )
