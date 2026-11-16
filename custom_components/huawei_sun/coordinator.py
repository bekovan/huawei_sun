"""DataUpdateCoordinator for the Huawei SUN2000 integration."""

from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING

from modbus_connection import ModbusError, ModbusTimeoutError
from modbus_connection.model import UpdateReport

from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, LOGGER, TIMEOUTS_BEFORE_DISCONNECT
from .vendor.huawei_modbus import MANUFACTURER, MODEL

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable
    from datetime import timedelta

    from homeassistant.core import HomeAssistant

    from .data import HuaweiSunConfigEntry
    from .vendor.huawei_modbus import HuaweiSun2000


class HuaweiSunCoordinator(DataUpdateCoordinator[UpdateReport]):
    """Poll one inverter and hand the update report to the entities."""

    config_entry: HuaweiSunConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        entry: HuaweiSunConfigEntry,
        device: HuaweiSun2000,
        poll: Callable[[], Awaitable[UpdateReport]],
        interval: timedelta,
    ) -> None:
        """Initialize the coordinator for one inverter."""
        super().__init__(
            hass,
            LOGGER,
            config_entry=entry,
            name=entry.title,
            update_interval=interval,
        )
        self.device = device
        self._poll = poll
        self._timeouts = 0
        self._failed: frozenset[str] = frozenset()

    @cached_property
    def device_info(self) -> DeviceInfo:
        """Describe the inverter to the device registry."""
        identity = self.device.identity
        serial_number = identity.serial_number
        return DeviceInfo(
            identifiers={(DOMAIN, serial_number or self.config_entry.entry_id)},
            manufacturer=MANUFACTURER,
            model=identity.model_name or MODEL,
            sw_version=identity.software_version or identity.firmware_version,
            serial_number=serial_number,
            name=self.config_entry.title,
        )

    async def async_write(self, component: str, field: str, value: object) -> None:
        """Write one setting and refresh the poll so entities follow it."""
        block = getattr(self.device, component, None)
        if block is None:
            message = f"Setting {field!r} is not available on this device"
            raise HomeAssistantError(message)
        try:
            await block.write(field, value)
        except (AttributeError, ValueError) as err:
            raise HomeAssistantError(str(err)) from err
        await self.async_request_refresh()

    async def _async_update_data(self) -> UpdateReport:
        """Poll the inverter and report what refreshed."""
        try:
            report = await self._poll()
        except ModbusTimeoutError as err:
            self._timeouts += 1
            if self._timeouts >= TIMEOUTS_BEFORE_DISCONNECT:
                # A bridge that keeps the socket open while the inverter stopped
                # answering never reconnects on its own, so recycle the link.
                LOGGER.debug("Recycling the Modbus link after repeated timeouts")
                await self.device.modbus_unit.disconnect()
                self._timeouts = 0
            message = f"No answer from the inverter: {err}"
            raise UpdateFailed(message) from err
        except ModbusError as err:
            raise UpdateFailed(str(err)) from err

        self._timeouts = 0
        if not report.updated:
            first = next(iter(report.failed.values()), None)
            message = f"No data from the inverter: {first}"
            raise UpdateFailed(message) from first
        for name in sorted(report.failed.keys() - self._failed):
            LOGGER.warning("Could not refresh %s: %s", name, report.failed[name])
        self._failed = frozenset(report.failed)
        return report
