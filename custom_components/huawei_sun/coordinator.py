"""DataUpdateCoordinator for the Huawei SUN2000 integration."""

from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING

from modbus_connection import ModbusError, ModbusTimeoutError
from modbus_connection.model import UpdateReport

from homeassistant.core import callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import device_registry as dr
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
        self._inverter_device_id: str | None = None

    @cached_property
    def inverter_identifier(self) -> tuple[str, str]:
        """Registry identifier of the inverter device."""
        serial_number = self.device.identity.serial_number
        return (DOMAIN, serial_number or self.config_entry.entry_id)

    @cached_property
    def device_info(self) -> DeviceInfo:
        """Describe the inverter to the device registry."""
        identity = self.device.identity
        serial_number = identity.serial_number
        return DeviceInfo(
            identifiers={self.inverter_identifier},
            manufacturer=MANUFACTURER,
            model=identity.model_name or MODEL,
            sw_version=identity.software_version or identity.firmware_version,
            serial_number=serial_number,
            name=self.config_entry.title,
        )

    @callback
    def register_devices(self, hass: HomeAssistant) -> None:
        """Register the inverter before entities attach, so the battery can link."""
        inverter = dr.async_get(hass).async_get_or_create(
            config_entry_id=self.config_entry.entry_id,
            **self.device_info,
        )
        self._inverter_device_id = inverter.id

    @cached_property
    def battery_device_info(self) -> DeviceInfo:
        """Describe the attached LUNA2000 as a device of its own."""
        battery = self.device.battery
        serial_number: str | None = None
        if battery is not None and battery.serial_number:
            serial_number = battery.serial_number.strip() or None
        identifier = serial_number or f"{self.config_entry.entry_id}_battery"
        return DeviceInfo(
            identifiers={(DOMAIN, identifier)},
            manufacturer=MANUFACTURER,
            model="LUNA2000",
            serial_number=serial_number,
            name="LUNA2000",
            via_device_id=self._inverter_device_id,
        )

    @cached_property
    def meter_device_info(self) -> DeviceInfo:
        """Describe the external grid meter as a device of its own."""
        inverter_serial = self.device.identity.serial_number
        identifier = f"{inverter_serial or self.config_entry.entry_id}_meter"
        return DeviceInfo(
            identifiers={(DOMAIN, identifier)},
            manufacturer=MANUFACTURER,
            model="Power meter",
            name="Power meter",
            via_device_id=self._inverter_device_id,
        )

    def device_info_for(self, component: str) -> DeviceInfo:
        """Return the device that owns one entity's register block."""
        if component.startswith("battery"):
            return self.battery_device_info
        if component.startswith("grid_meter"):
            return self.meter_device_info
        return self.device_info

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
