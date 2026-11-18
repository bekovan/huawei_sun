"""Set up the Huawei SUN2000 integration."""

from datetime import timedelta
from typing import TYPE_CHECKING

from homeassistant.components.modbus import async_get_unit
from homeassistant.const import Platform

from .config_flow import connection_params
from .const import CONF_SCAN_INTERVAL, CONF_UNIT_ID, DEFAULT_SCAN_INTERVAL
from .coordinator import HuaweiSunCoordinator
from .data import HuaweiSunData
from .vendor.huawei_modbus import HuaweiSun2000

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .data import HuaweiSunConfigEntry

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.NUMBER,
    Platform.SELECT,
    Platform.SWITCH,
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: HuaweiSunConfigEntry,
) -> bool:
    """Set up one inverter from a config entry."""
    # The connection is shared between integrations and owned by the modbus
    # integration, which releases this unit when the entry unloads. There is
    # nothing to disconnect here.
    unit = async_get_unit(
        hass,
        entry,
        connection_params(entry.data),
        int(entry.data[CONF_UNIT_ID]),
    )
    device = HuaweiSun2000(unit)

    interval = timedelta(
        seconds=entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
    )
    coordinator = HuaweiSunCoordinator(
        hass, entry, device, device.async_update, interval
    )
    # The first read establishes the link; a failure becomes ConfigEntryNotReady.
    await coordinator.async_config_entry_first_refresh()

    # Register the inverter device up front; the battery links to its registry id.
    coordinator.register_devices(hass)

    entry.runtime_data = HuaweiSunData(coordinator=coordinator)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: HuaweiSunConfigEntry,
) -> bool:
    """Unload one inverter and release its unit."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
