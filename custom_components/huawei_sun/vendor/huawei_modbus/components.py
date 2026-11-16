"""
Register map for a SUN2000 L1 inverter and an attached LUNA2000 battery.

The addresses are the decimal register numbers from the Huawei SUN2000 Modbus
interface definition. Huawei serves both the 32xxx telemetry block and the
47xxx settings block through holding registers (function code 3), which is why
every component below keeps the default ``register_space``.

Only registers that are read or written by this integration are declared. To
expose another register, add a field here and wire it into an entity platform;
the shared connection planner will fold it into the nearest read block.
"""

from collections.abc import Callable, Iterable

from modbus_connection.model import (
    Component,
    WriteValidator,
    boolean,
    gauge,
    int32,
    integer,
    string,
    uint32,
)

# ---------------------------------------------------------------------------
# Write validators
#
# These reject nonsensical values before anything reaches the inverter. Home
# Assistant's number and select widgets already constrain the UI, but service
# calls can bypass a widget, so the library enforces the same bounds.
# ---------------------------------------------------------------------------


def _number_between(
    minimum: float,
    maximum: float,
    name: str,
) -> WriteValidator:
    """Build a validator that keeps a scaled number inside a range."""

    def validate(value: object) -> float:
        number = float(value)  # type: ignore[arg-type]
        if not minimum <= number <= maximum:
            message = f"{name} must be between {minimum} and {maximum}"
            raise ValueError(message)
        return number

    return validate


def _integer_between(
    minimum: int,
    maximum: int,
    name: str,
) -> WriteValidator:
    """Build a validator that keeps an integer inside a range."""

    def validate(value: object) -> int:
        number = int(value)  # type: ignore[arg-type]
        if not minimum <= number <= maximum:
            message = f"{name} must be between {minimum} and {maximum}"
            raise ValueError(message)
        return number

    return validate


def _one_of(allowed: Iterable[int], name: str) -> WriteValidator:
    """Build a validator that only accepts the listed register values."""
    choices = frozenset(allowed)

    def validate(value: object) -> int:
        number = int(value)  # type: ignore[arg-type]
        if number not in choices:
            choices_text = ", ".join(str(choice) for choice in sorted(choices))
            message = f"{name} must be one of {choices_text}"
            raise ValueError(message)
        return number

    return validate


POWER_LIMIT = _integer_between(0, 20_000, "Battery power limit")
PERCENTAGE = _number_between(0, 100, "Percentage")
SOC = _number_between(0, 100, "State of charge")
FORCED_PERIOD = _integer_between(0, 1_440, "Forced charge/discharge period")
WORKING_MODE = _one_of(range(7), "Battery working mode")
FORCIBLE_ACTION = _one_of(range(3), "Forced charge/discharge action")
FORCIBLE_TARGET = _one_of(range(2), "Forced charge/discharge target mode")


# ---------------------------------------------------------------------------
# Inverter
# ---------------------------------------------------------------------------


class InverterProbe(Component):
    """The smallest read that identifies an inverter during the config flow."""

    model_name = string(30000, 15)
    serial_number = string(30015, 10)


class InverterIdentity(Component):
    """Static identification and rating data, read once after setup."""

    model_name = string(30000, 15)
    serial_number = string(30015, 10)
    product_number = string(30025, 10)
    firmware_version = string(30035, 15)
    software_version = string(30050, 15)
    pv_string_count = integer(30071, signed=False)
    rated_power = uint32(30073, unit="W")
    max_active_power = uint32(30075, unit="W")


class InverterTelemetry(Component):
    """Live AC, DC and yield data from the inverter."""

    state_1 = integer(32000, signed=False)
    pv1_voltage = gauge(32016, 0.1, signed=True, unit="V")
    pv1_current = gauge(32017, 0.01, signed=True, unit="A")
    pv2_voltage = gauge(32018, 0.1, signed=True, unit="V")
    pv2_current = gauge(32019, 0.01, signed=True, unit="A")

    input_power = int32(32064, unit="W")
    line_voltage_ab = gauge(32066, 0.1, signed=False, unit="V")
    line_voltage_bc = gauge(32067, 0.1, signed=False, unit="V")
    line_voltage_ca = gauge(32068, 0.1, signed=False, unit="V")
    phase_a_voltage = gauge(32069, 0.1, signed=False, unit="V")
    phase_b_voltage = gauge(32070, 0.1, signed=False, unit="V")
    phase_c_voltage = gauge(32071, 0.1, signed=False, unit="V")
    phase_a_current = int32(32072, scale=0.001, unit="A")
    phase_b_current = int32(32074, scale=0.001, unit="A")
    phase_c_current = int32(32076, scale=0.001, unit="A")
    active_power = int32(32080, unit="W")
    reactive_power = int32(32082, unit="var")
    power_factor = gauge(32084, 0.001, signed=True)
    grid_frequency = gauge(32085, 0.01, signed=False, unit="Hz")
    efficiency = gauge(32086, 0.01, signed=False, unit="%")
    internal_temperature = gauge(32087, 0.1, signed=True, unit="°C")
    device_status = integer(32089, signed=False)

    # Alarm bitfields. The entity layer exposes "any alarm" as a problem binary
    # sensor; the raw words stay available for diagnostics.
    alarm_1 = integer(32008, signed=False)
    alarm_2 = integer(32009, signed=False)
    alarm_3 = integer(32010, signed=False)

    accumulated_yield_energy = uint32(32106, scale=0.01, unit="kWh")
    daily_yield_energy = uint32(32114, scale=0.01, unit="kWh")
    monthly_yield_energy = uint32(32116, scale=0.01, unit="kWh")
    yearly_yield_energy = uint32(32118, scale=0.01, unit="kWh")


class InverterSettings(Component):
    """Writable inverter limits."""

    active_power_limit = gauge(
        40125,
        0.1,
        signed=True,
        writable=PERCENTAGE,
        unit="%",
    )


# ---------------------------------------------------------------------------
# LUNA2000 battery
# ---------------------------------------------------------------------------


class Luna2000Telemetry(Component):
    """Live data for battery unit 1."""

    running_status = integer(37000, signed=False)
    charge_discharge_power = int32(37001, unit="W")
    bus_voltage = gauge(37003, 0.1, signed=False, unit="V")
    state_of_capacity = gauge(37004, 0.1, signed=False, unit="%")
    working_mode = integer(37006, signed=False)
    rated_charge_power = uint32(37007, unit="W")
    rated_discharge_power = uint32(37009, unit="W")
    fault_id = integer(37014, signed=False)
    day_charge = uint32(37015, scale=0.01, unit="kWh")
    day_discharge = uint32(37017, scale=0.01, unit="kWh")
    bus_current = gauge(37021, 0.1, signed=True, unit="A")
    battery_temperature = gauge(37022, 0.1, signed=True, unit="°C")
    serial_number = string(37052, 10)
    total_charge = uint32(37066, scale=0.01, unit="kWh")
    total_discharge = uint32(37068, scale=0.01, unit="kWh")


class Luna2000Overview(Component):
    """System-wide battery capacity and energy totals."""

    rated_capacity = uint32(37758, unit="Wh")
    state_of_capacity = gauge(37760, 0.1, signed=False, unit="%")
    bus_voltage = gauge(37763, 0.1, signed=False, unit="V")
    charge_discharge_power = int32(37765, unit="W")
    total_charge = uint32(37780, scale=0.01, unit="kWh")
    total_discharge = uint32(37782, scale=0.01, unit="kWh")
    day_charge = uint32(37784, scale=0.01, unit="kWh")
    day_discharge = uint32(37786, scale=0.01, unit="kWh")


class Luna2000Status(Component):
    """Connection state of battery unit 1."""

    connect_status = integer(37994, signed=False)


class Luna2000Settings(Component):
    """Writable battery settings, including the forced charge/discharge controls."""

    maximum_charging_power = uint32(
        47075,
        writable=POWER_LIMIT,
        unit="W",
    )
    maximum_discharging_power = uint32(
        47077,
        writable=POWER_LIMIT,
        unit="W",
    )
    charging_cutoff_soc = gauge(
        47081,
        0.1,
        signed=False,
        writable=SOC,
        unit="%",
    )
    discharging_cutoff_soc = gauge(
        47082,
        0.1,
        signed=False,
        writable=SOC,
        unit="%",
    )
    forced_period = integer(
        47083,
        signed=False,
        writable=FORCED_PERIOD,
        unit="min",
    )
    forced_power = int32(47084, unit="W")
    working_mode = integer(47086, signed=False, writable=WORKING_MODE)
    charge_from_grid = boolean(47087, writable=True)
    grid_charge_cutoff_soc = gauge(
        47088,
        0.1,
        signed=False,
        writable=SOC,
        unit="%",
    )
    forcible_charge_discharge = integer(
        47100,
        signed=False,
        writable=FORCIBLE_ACTION,
    )
    forcible_target_soc = gauge(
        47101,
        0.1,
        signed=False,
        writable=SOC,
        unit="%",
    )


class Luna2000ForcedSettings(Component):
    """
    Advanced forced charge/discharge controls.

    Kept apart from :class:`Luna2000Settings` because older firmware does not
    serve registers 47246-47249. A missing block disables only these entities,
    not the battery power limits and cutoffs.
    """

    forcible_setting_mode = integer(
        47246,
        signed=False,
        writable=FORCIBLE_TARGET,
    )
    forcible_charge_power = uint32(
        47247,
        writable=POWER_LIMIT,
        unit="W",
    )
    forcible_discharge_power = uint32(
        47249,
        writable=POWER_LIMIT,
        unit="W",
    )


#: Component attributes that are refreshed on every poll.
UPDATE_BLOCKS: tuple[str, ...] = (
    "telemetry",
    "battery",
    "battery_overview",
    "battery_status",
    "settings",
    "battery_settings",
    "battery_forced",
)

#: Component attributes included in a diagnostics dump.
DIAGNOSTIC_BLOCKS: tuple[str, ...] = ("identity", *UPDATE_BLOCKS)

SensorValue = float | int | str | None
"""A value a sensor description may return."""

ValueFn = Callable[[object], SensorValue]
"""A callable reading one attribute from the device object."""
