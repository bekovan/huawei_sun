"""Number platform for the Huawei SUN2000 integration."""

from dataclasses import dataclass
from typing import TYPE_CHECKING

from homeassistant.components.number import (
    NumberDeviceClass,
    NumberEntity,
    NumberEntityDescription,
    NumberMode,
)
from homeassistant.const import PERCENTAGE, EntityCategory, UnitOfPower, UnitOfTime

from .entity import HuaweiSunEntity

if TYPE_CHECKING:
    from collections.abc import Callable

    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import HuaweiSunCoordinator
    from .data import HuaweiSunConfigEntry
    from .vendor.huawei_modbus import HuaweiSun2000


@dataclass(frozen=True, kw_only=True)
class HuaweiNumberEntityDescription(NumberEntityDescription):
    """Describe a writable setting backed by one device register."""

    component: str
    """Device attribute that holds the block this setting belongs to."""
    report_name: str
    """Name of the block in the coordinator's update report."""
    field: str
    """Field name inside that block."""
    value_fn: Callable[[HuaweiSun2000], float | int | None]


NUMBERS: tuple[HuaweiNumberEntityDescription, ...] = (
    HuaweiNumberEntityDescription(
        key="active_power_limit",
        translation_key="active_power_limit",
        component="settings",
        report_name="settings",
        field="active_power_limit",
        native_min_value=0,
        native_max_value=100,
        native_step=0.1,
        native_unit_of_measurement=PERCENTAGE,
        mode=NumberMode.BOX,
        entity_category=EntityCategory.CONFIG,
        icon="mdi:transmission-tower-export",
        value_fn=lambda device: (
            device.settings.active_power_limit if device.settings else None
        ),
    ),
    HuaweiNumberEntityDescription(
        key="battery_max_charging_power",
        translation_key="battery_max_charging_power",
        component="battery_settings",
        report_name="battery_settings",
        field="maximum_charging_power",
        native_min_value=0,
        native_max_value=20_000,
        native_step=100,
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=NumberDeviceClass.POWER,
        mode=NumberMode.BOX,
        entity_category=EntityCategory.CONFIG,
        value_fn=lambda device: (
            device.battery_settings.maximum_charging_power
            if device.battery_settings
            else None
        ),
    ),
    HuaweiNumberEntityDescription(
        key="battery_max_discharging_power",
        translation_key="battery_max_discharging_power",
        component="battery_settings",
        report_name="battery_settings",
        field="maximum_discharging_power",
        native_min_value=0,
        native_max_value=20_000,
        native_step=100,
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=NumberDeviceClass.POWER,
        mode=NumberMode.BOX,
        entity_category=EntityCategory.CONFIG,
        value_fn=lambda device: (
            device.battery_settings.maximum_discharging_power
            if device.battery_settings
            else None
        ),
    ),
    HuaweiNumberEntityDescription(
        key="battery_charging_cutoff_soc",
        translation_key="battery_charging_cutoff_soc",
        component="battery_settings",
        report_name="battery_settings",
        field="charging_cutoff_soc",
        native_min_value=0,
        native_max_value=100,
        native_step=0.1,
        native_unit_of_measurement=PERCENTAGE,
        mode=NumberMode.BOX,
        entity_category=EntityCategory.CONFIG,
        icon="mdi:battery-arrow-up",
        value_fn=lambda device: (
            device.battery_settings.charging_cutoff_soc
            if device.battery_settings
            else None
        ),
    ),
    HuaweiNumberEntityDescription(
        key="battery_discharging_cutoff_soc",
        translation_key="battery_discharging_cutoff_soc",
        component="battery_settings",
        report_name="battery_settings",
        field="discharging_cutoff_soc",
        native_min_value=0,
        native_max_value=100,
        native_step=0.1,
        native_unit_of_measurement=PERCENTAGE,
        mode=NumberMode.BOX,
        entity_category=EntityCategory.CONFIG,
        icon="mdi:battery-arrow-down",
        value_fn=lambda device: (
            device.battery_settings.discharging_cutoff_soc
            if device.battery_settings
            else None
        ),
    ),
    HuaweiNumberEntityDescription(
        key="battery_grid_charge_cutoff_soc",
        translation_key="battery_grid_charge_cutoff_soc",
        component="battery_settings",
        report_name="battery_settings",
        field="grid_charge_cutoff_soc",
        native_min_value=0,
        native_max_value=100,
        native_step=0.1,
        native_unit_of_measurement=PERCENTAGE,
        mode=NumberMode.BOX,
        entity_category=EntityCategory.CONFIG,
        icon="mdi:transmission-tower-import",
        value_fn=lambda device: (
            device.battery_settings.grid_charge_cutoff_soc
            if device.battery_settings
            else None
        ),
    ),
    HuaweiNumberEntityDescription(
        key="battery_grid_charge_maximum_power",
        translation_key="battery_grid_charge_maximum_power",
        component="battery_settings",
        report_name="battery_settings",
        field="grid_charge_maximum_power",
        native_min_value=0,
        native_max_value=20_000,
        native_step=100,
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=NumberDeviceClass.POWER,
        mode=NumberMode.BOX,
        entity_category=EntityCategory.CONFIG,
        icon="mdi:transmission-tower-import",
        value_fn=lambda device: (
            device.battery_settings.grid_charge_maximum_power
            if device.battery_settings
            else None
        ),
    ),
    HuaweiNumberEntityDescription(
        key="battery_peak_shaving_soc",
        translation_key="battery_peak_shaving_soc",
        component="battery_peak_shaving",
        report_name="battery_peak_shaving",
        field="peak_shaving_soc",
        native_min_value=0,
        native_max_value=100,
        native_step=0.1,
        native_unit_of_measurement=PERCENTAGE,
        mode=NumberMode.BOX,
        entity_category=EntityCategory.CONFIG,
        icon="mdi:battery-arrow-up",
        value_fn=lambda device: (
            device.battery_peak_shaving.peak_shaving_soc
            if device.battery_peak_shaving
            else None
        ),
    ),
    HuaweiNumberEntityDescription(
        key="battery_forced_period",
        translation_key="battery_forced_period",
        component="battery_settings",
        report_name="battery_settings",
        field="forced_period",
        native_min_value=0,
        native_max_value=1440,
        native_step=1,
        native_unit_of_measurement=UnitOfTime.MINUTES,
        mode=NumberMode.BOX,
        entity_category=EntityCategory.CONFIG,
        icon="mdi:timer-outline",
        value_fn=lambda device: (
            device.battery_settings.forced_period if device.battery_settings else None
        ),
    ),
    HuaweiNumberEntityDescription(
        key="battery_forcible_target_soc",
        translation_key="battery_forcible_target_soc",
        component="battery_settings",
        report_name="battery_settings",
        field="forcible_target_soc",
        native_min_value=0,
        native_max_value=100,
        native_step=0.1,
        native_unit_of_measurement=PERCENTAGE,
        mode=NumberMode.BOX,
        entity_category=EntityCategory.CONFIG,
        icon="mdi:battery-target",
        value_fn=lambda device: (
            device.battery_settings.forcible_target_soc
            if device.battery_settings
            else None
        ),
    ),
    HuaweiNumberEntityDescription(
        key="battery_forcible_charge_power",
        translation_key="battery_forcible_charge_power",
        component="battery_forced",
        report_name="battery_forced",
        field="forcible_charge_power",
        native_min_value=0,
        native_max_value=20_000,
        native_step=100,
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=NumberDeviceClass.POWER,
        mode=NumberMode.BOX,
        entity_category=EntityCategory.CONFIG,
        value_fn=lambda device: (
            device.battery_forced.forcible_charge_power
            if device.battery_forced
            else None
        ),
    ),
    HuaweiNumberEntityDescription(
        key="battery_forcible_discharge_power",
        translation_key="battery_forcible_discharge_power",
        component="battery_forced",
        report_name="battery_forced",
        field="forcible_discharge_power",
        native_min_value=0,
        native_max_value=20_000,
        native_step=100,
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=NumberDeviceClass.POWER,
        mode=NumberMode.BOX,
        entity_category=EntityCategory.CONFIG,
        value_fn=lambda device: (
            device.battery_forced.forcible_discharge_power
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
    """Set up the writable number entities of one inverter."""
    coordinator = entry.runtime_data.coordinator
    async_add_entities(
        HuaweiSunNumber(coordinator, description)
        for description in NUMBERS
        if getattr(coordinator.device, description.component, None) is not None
    )


class HuaweiSunNumber(HuaweiSunEntity, NumberEntity):
    """A writable setting read from and written to one register."""

    entity_description: HuaweiNumberEntityDescription

    def __init__(
        self,
        coordinator: HuaweiSunCoordinator,
        description: HuaweiNumberEntityDescription,
    ) -> None:
        """Initialize the setting."""
        super().__init__(coordinator, description.component)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{description.key}"

    @property
    def native_value(self) -> float | int | None:
        """Return the current setting."""
        return self.entity_description.value_fn(self.coordinator.device)

    async def async_set_native_value(self, value: float) -> None:
        """Write the setting and refresh the coordinator."""
        await self.coordinator.async_write(
            self.entity_description.component,
            self.entity_description.field,
            value,
        )
