"""Sensor platform for the Huawei SUN2000 integration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from homeassistant.components.sensor import (
    RestoreSensor,
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    PERCENTAGE,
    EntityCategory,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfFrequency,
    UnitOfPower,
    UnitOfReactivePower,
    UnitOfTemperature,
)
from homeassistant.core import callback

from .entity import HuaweiSunEntity
from .vendor.huawei_modbus.values import (
    DEVICE_STATUS,
    STORAGE_STATUS,
    STORAGE_WORKING_MODE_B,
    label,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import HuaweiSunCoordinator
    from .data import HuaweiSunConfigEntry
    from .vendor.huawei_modbus import HuaweiSun2000

SENSOR_VALUE = float | int | str | None


@dataclass(frozen=True, kw_only=True)
class HuaweiSensorEntityDescription(SensorEntityDescription):
    """Describe a sensor backed by one device attribute."""

    component: str
    """Device attribute that holds the block this sensor reads."""
    report_name: str
    """Name of the block in the coordinator's update report."""
    value_fn: Callable[[HuaweiSun2000], SENSOR_VALUE]


SENSORS: tuple[HuaweiSensorEntityDescription, ...] = (
    # -- Inverter telemetry -------------------------------------------------
    HuaweiSensorEntityDescription(
        key="pv1_voltage",
        translation_key="pv1_voltage",
        component="telemetry",
        report_name="telemetry",
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        value_fn=lambda device: device.telemetry.pv1_voltage,
    ),
    HuaweiSensorEntityDescription(
        key="pv1_current",
        translation_key="pv1_current",
        component="telemetry",
        report_name="telemetry",
        device_class=SensorDeviceClass.CURRENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
        value_fn=lambda device: device.telemetry.pv1_current,
    ),
    HuaweiSensorEntityDescription(
        key="pv2_voltage",
        translation_key="pv2_voltage",
        component="telemetry",
        report_name="telemetry",
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        value_fn=lambda device: device.telemetry.pv2_voltage,
    ),
    HuaweiSensorEntityDescription(
        key="pv2_current",
        translation_key="pv2_current",
        component="telemetry",
        report_name="telemetry",
        device_class=SensorDeviceClass.CURRENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
        value_fn=lambda device: device.telemetry.pv2_current,
    ),
    HuaweiSensorEntityDescription(
        key="input_power",
        translation_key="input_power",
        component="telemetry",
        report_name="telemetry",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
        value_fn=lambda device: device.telemetry.input_power,
    ),
    HuaweiSensorEntityDescription(
        key="phase_a_voltage",
        translation_key="phase_a_voltage",
        component="telemetry",
        report_name="telemetry",
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        value_fn=lambda device: device.telemetry.phase_a_voltage,
    ),
    HuaweiSensorEntityDescription(
        key="phase_b_voltage",
        translation_key="phase_b_voltage",
        component="telemetry",
        report_name="telemetry",
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        value_fn=lambda device: device.telemetry.phase_b_voltage,
    ),
    HuaweiSensorEntityDescription(
        key="phase_c_voltage",
        translation_key="phase_c_voltage",
        component="telemetry",
        report_name="telemetry",
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        value_fn=lambda device: device.telemetry.phase_c_voltage,
    ),
    HuaweiSensorEntityDescription(
        key="phase_a_current",
        translation_key="phase_a_current",
        component="telemetry",
        report_name="telemetry",
        device_class=SensorDeviceClass.CURRENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
        value_fn=lambda device: device.telemetry.phase_a_current,
    ),
    HuaweiSensorEntityDescription(
        key="phase_b_current",
        translation_key="phase_b_current",
        component="telemetry",
        report_name="telemetry",
        device_class=SensorDeviceClass.CURRENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
        value_fn=lambda device: device.telemetry.phase_b_current,
    ),
    HuaweiSensorEntityDescription(
        key="phase_c_current",
        translation_key="phase_c_current",
        component="telemetry",
        report_name="telemetry",
        device_class=SensorDeviceClass.CURRENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
        value_fn=lambda device: device.telemetry.phase_c_current,
    ),
    HuaweiSensorEntityDescription(
        key="active_power",
        translation_key="active_power",
        component="telemetry",
        report_name="telemetry",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
        value_fn=lambda device: device.telemetry.active_power,
    ),
    HuaweiSensorEntityDescription(
        key="reactive_power",
        translation_key="reactive_power",
        component="telemetry",
        report_name="telemetry",
        device_class=SensorDeviceClass.REACTIVE_POWER,
        native_unit_of_measurement=UnitOfReactivePower.VOLT_AMPERE_REACTIVE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
        value_fn=lambda device: device.telemetry.reactive_power,
    ),
    HuaweiSensorEntityDescription(
        key="power_factor",
        translation_key="power_factor",
        component="telemetry",
        report_name="telemetry",
        device_class=SensorDeviceClass.POWER_FACTOR,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=3,
        value_fn=lambda device: device.telemetry.power_factor,
    ),
    HuaweiSensorEntityDescription(
        key="grid_frequency",
        translation_key="grid_frequency",
        component="telemetry",
        report_name="telemetry",
        device_class=SensorDeviceClass.FREQUENCY,
        native_unit_of_measurement=UnitOfFrequency.HERTZ,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
        value_fn=lambda device: device.telemetry.grid_frequency,
    ),
    HuaweiSensorEntityDescription(
        key="efficiency",
        translation_key="efficiency",
        component="telemetry",
        report_name="telemetry",
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:percent",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
        value_fn=lambda device: device.telemetry.efficiency,
    ),
    HuaweiSensorEntityDescription(
        key="internal_temperature",
        translation_key="internal_temperature",
        component="telemetry",
        report_name="telemetry",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        value_fn=lambda device: device.telemetry.internal_temperature,
    ),
    HuaweiSensorEntityDescription(
        key="device_status",
        translation_key="device_status",
        component="telemetry",
        report_name="telemetry",
        icon="mdi:solar-power-variant",
        value_fn=lambda device: label(DEVICE_STATUS, device.telemetry.device_status),
    ),
    HuaweiSensorEntityDescription(
        key="accumulated_yield_energy",
        translation_key="accumulated_yield_energy",
        component="telemetry",
        report_name="telemetry",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        suggested_display_precision=2,
        value_fn=lambda device: device.telemetry.accumulated_yield_energy,
    ),
    HuaweiSensorEntityDescription(
        key="daily_yield_energy",
        translation_key="daily_yield_energy",
        component="telemetry",
        report_name="telemetry",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        suggested_display_precision=2,
        value_fn=lambda device: device.telemetry.daily_yield_energy,
    ),
    HuaweiSensorEntityDescription(
        key="monthly_yield_energy",
        translation_key="monthly_yield_energy",
        component="telemetry",
        report_name="telemetry",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        suggested_display_precision=2,
        value_fn=lambda device: device.telemetry.monthly_yield_energy,
    ),
    HuaweiSensorEntityDescription(
        key="yearly_yield_energy",
        translation_key="yearly_yield_energy",
        component="telemetry",
        report_name="telemetry",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        suggested_display_precision=2,
        value_fn=lambda device: device.telemetry.yearly_yield_energy,
    ),
    # -- Battery unit 1 -----------------------------------------------------
    HuaweiSensorEntityDescription(
        key="battery_state_of_capacity",
        translation_key="battery_state_of_capacity",
        component="battery",
        report_name="battery",
        device_class=SensorDeviceClass.BATTERY,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        value_fn=lambda device: device.battery.state_of_capacity,  # type: ignore[union-attr]
    ),
    HuaweiSensorEntityDescription(
        key="battery_power",
        translation_key="battery_power",
        component="battery",
        report_name="battery",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
        value_fn=lambda device: device.battery.charge_discharge_power,  # type: ignore[union-attr]
    ),
    HuaweiSensorEntityDescription(
        key="battery_bus_voltage",
        translation_key="battery_bus_voltage",
        component="battery",
        report_name="battery",
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        value_fn=lambda device: device.battery.bus_voltage,  # type: ignore[union-attr]
    ),
    HuaweiSensorEntityDescription(
        key="battery_bus_current",
        translation_key="battery_bus_current",
        component="battery",
        report_name="battery",
        device_class=SensorDeviceClass.CURRENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
        value_fn=lambda device: device.battery.bus_current,  # type: ignore[union-attr]
    ),
    HuaweiSensorEntityDescription(
        key="battery_temperature",
        translation_key="battery_temperature",
        component="battery",
        report_name="battery",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        value_fn=lambda device: device.battery.battery_temperature,  # type: ignore[union-attr]
    ),
    HuaweiSensorEntityDescription(
        key="battery_running_status",
        translation_key="battery_running_status",
        component="battery",
        report_name="battery",
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:battery-heart-variant",
        value_fn=lambda device: label(STORAGE_STATUS, device.battery.running_status),  # type: ignore[union-attr]
    ),
    HuaweiSensorEntityDescription(
        key="battery_working_mode",
        translation_key="battery_working_mode",
        component="battery",
        report_name="battery",
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:battery-sync",
        value_fn=lambda device: label(
            STORAGE_WORKING_MODE_B,
            device.battery.working_mode,  # type: ignore[union-attr]
        ),
    ),
    HuaweiSensorEntityDescription(
        key="battery_rated_charge_power",
        translation_key="battery_rated_charge_power",
        component="battery",
        report_name="battery",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda device: device.battery.rated_charge_power,  # type: ignore[union-attr]
    ),
    HuaweiSensorEntityDescription(
        key="battery_rated_discharge_power",
        translation_key="battery_rated_discharge_power",
        component="battery",
        report_name="battery",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda device: device.battery.rated_discharge_power,  # type: ignore[union-attr]
    ),
    HuaweiSensorEntityDescription(
        key="battery_day_charge",
        translation_key="battery_day_charge",
        component="battery",
        report_name="battery",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        suggested_display_precision=2,
        value_fn=lambda device: device.battery.day_charge,  # type: ignore[union-attr]
    ),
    HuaweiSensorEntityDescription(
        key="battery_day_discharge",
        translation_key="battery_day_discharge",
        component="battery",
        report_name="battery",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        suggested_display_precision=2,
        value_fn=lambda device: device.battery.day_discharge,  # type: ignore[union-attr]
    ),
    HuaweiSensorEntityDescription(
        key="battery_total_charge",
        translation_key="battery_total_charge",
        component="battery",
        report_name="battery",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        suggested_display_precision=2,
        value_fn=lambda device: device.battery.total_charge,  # type: ignore[union-attr]
    ),
    HuaweiSensorEntityDescription(
        key="battery_total_discharge",
        translation_key="battery_total_discharge",
        component="battery",
        report_name="battery",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        suggested_display_precision=2,
        value_fn=lambda device: device.battery.total_discharge,  # type: ignore[union-attr]
    ),
    HuaweiSensorEntityDescription(
        key="battery_rated_capacity",
        translation_key="battery_rated_capacity",
        component="battery_overview",
        report_name="battery_overview",
        device_class=SensorDeviceClass.ENERGY_STORAGE,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        entity_category=EntityCategory.DIAGNOSTIC,
        suggested_display_precision=2,
        value_fn=lambda device: (
            device.battery_overview.rated_capacity / 1000  # type: ignore[union-attr]
            if device.battery_overview is not None
            else None
        ),
    ),
)


async def async_setup_entry(
    _hass: HomeAssistant,
    entry: HuaweiSunConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensors of one inverter."""
    coordinator = entry.runtime_data.coordinator
    async_add_entities(
        (
            HuaweiSunEnergySensor
            if description.state_class
            in (SensorStateClass.TOTAL, SensorStateClass.TOTAL_INCREASING)
            else HuaweiSunSensor
        )(coordinator, description)
        for description in SENSORS
        if getattr(coordinator.device, description.component, None) is not None
    )


class HuaweiSunSensor(HuaweiSunEntity, SensorEntity):
    """A measurement read from one of the device's register blocks."""

    entity_description: HuaweiSensorEntityDescription

    def __init__(
        self,
        coordinator: HuaweiSunCoordinator,
        description: HuaweiSensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{description.key}"

    @property
    def native_value(self) -> SENSOR_VALUE:
        """Return the current value."""
        return self.entity_description.value_fn(self.coordinator.device)


class HuaweiSunEnergySensor(HuaweiSunEntity, RestoreSensor):
    """
    Lifetime energy: keeps its value while the inverter sleeps.

    An inverter powers down every night. A gap in a long-term statistic damages
    the energy dashboard, so this sensor stays available, holds its last value,
    and restores it after Home Assistant restarts.
    """

    entity_description: HuaweiSensorEntityDescription

    def __init__(
        self,
        coordinator: HuaweiSunCoordinator,
        description: HuaweiSensorEntityDescription,
    ) -> None:
        """Initialize the lifetime energy sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{description.key}"

    @property
    def available(self) -> bool:
        """Stay available while the inverter is offline."""
        return True

    async def async_added_to_hass(self) -> None:
        """Restore the last known value before the first poll lands."""
        await super().async_added_to_hass()
        if (last_data := await self.async_get_last_sensor_data()) is not None:
            self._attr_native_value = last_data.native_value
        self._process_data()

    @callback
    def _handle_coordinator_update(self) -> None:
        """Fold a new poll into the restored value."""
        self._process_data()
        super()._handle_coordinator_update()

    def _process_data(self) -> None:
        """Take a new reading unless the device returned nothing."""
        value = self.entity_description.value_fn(self.coordinator.device)
        if value is None:
            return
        last = self._attr_native_value
        if (
            self.entity_description.state_class is SensorStateClass.TOTAL_INCREASING
            and isinstance(last, int | float)
            and isinstance(value, int | float)
            and last * 0.99 <= value < last
        ):
            return  # ignore a minor decrease some firmware revisions report
        self._attr_native_value = value
