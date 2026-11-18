"""Diagnostics support for the Huawei SUN2000 integration."""

from typing import TYPE_CHECKING, Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.const import CONF_HOST
from modbus_connection import ModbusError

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .data import HuaweiSunConfigEntry

TO_REDACT = {CONF_HOST}

#: Register ranges that carry a serial number and are replaced in the dump.
SERIAL_REGISTERS: tuple[tuple[int, int], ...] = (
    (30015, 30024),  # inverter serial number
    (37052, 37061),  # battery unit serial number
)


def _is_serial_register(address: int) -> bool:
    """Whether a register address is inside a serial-number range."""
    return any(start <= address <= end for start, end in SERIAL_REGISTERS)


def _redact_registers(
    registers: dict[str, dict[int, int | bool]],
) -> dict[str, dict[int, int | bool | str]]:
    """Replace serial-number registers with a redaction marker."""
    return {
        block: {
            address: "**REDACTED**" if _is_serial_register(address) else value
            for address, value in block_registers.items()
        }
        for block, block_registers in registers.items()
    }


async def async_get_config_entry_diagnostics(
    _hass: HomeAssistant,
    entry: HuaweiSunConfigEntry,
) -> dict[str, Any]:
    """Return identity, report state and raw registers for a bug report."""
    coordinator = entry.runtime_data.coordinator
    device = coordinator.device
    report = coordinator.data

    registers: dict[str, dict[int, int | bool]] = {}
    read_error: str | None = None
    try:
        registers = await device.async_read_raw()
    except ModbusError as err:
        read_error = str(err)

    identity = device.identity
    return {
        "entry_data": async_redact_data(dict(entry.data), TO_REDACT),
        "entry_options": dict(entry.options),
        "identity": {
            "model_name": identity.model_name,
            "product_number": identity.product_number,
            "firmware_version": identity.firmware_version,
            "software_version": identity.software_version,
            "pv_string_count": identity.pv_string_count,
            "rated_power": identity.rated_power,
            "max_active_power": identity.max_active_power,
            "serial_number": "**REDACTED**",
        },
        "battery_present": device.battery_present,
        "last_update_success": coordinator.last_update_success,
        "updated": sorted(report.updated) if report else [],
        "failed": {name: str(err) for name, err in report.failed.items()}
        if report
        else {},
        "registers": _redact_registers(registers),
        "read_error": read_error,
    }
