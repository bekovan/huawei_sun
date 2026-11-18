"""
The top-level device object for a Huawei SUN2000 L1 inverter.

The inverter and an attached LUNA2000 battery are one Modbus device: the
battery registers belong to the inverter's holding-register map, so both share
a single ``ModbusUnit``.

The battery, the inverter's writable settings block and the advanced forced
charge/discharge registers are all optional. Firmware and hardware differ in
which they serve, so setup probes each block once with ``read_optional`` and
leaves the attribute ``None`` when the device rejects it. A poll then skips it,
and the integration creates no entities for it.
"""

from collections.abc import Iterable

from modbus_connection import ModbusUnit
from modbus_connection.model import Device, Raw, UpdateReport, read_optional

from .components import (
    DIAGNOSTIC_BLOCKS,
    UPDATE_BLOCKS,
    GridMeter,
    InverterIdentity,
    InverterSettings,
    InverterTelemetry,
    Luna2000ForcedSettings,
    Luna2000Overview,
    Luna2000PeakShaving,
    Luna2000Settings,
    Luna2000Status,
    Luna2000Telemetry,
)

MANUFACTURER = "Huawei"
"""Name the device reports in the Home Assistant device registry."""

MODEL = "SUN2000-3.68KTL-L1"
"""Model this register map was written for."""

#: A Huawei inverter can take several seconds to answer while it assembles a
#: block; the link's default request timeout is too tight for it.
REQUIRED_TIMEOUT = 15.0

#: Every component a diagnostics dump reads.
ALL: tuple[str, ...] = DIAGNOSTIC_BLOCKS


class HuaweiSun2000(Device):
    """A SUN2000 L1 inverter and the LUNA2000 battery attached to it."""

    def __init__(self, unit: ModbusUnit) -> None:
        """Bind the device to one unit on a shared Modbus connection."""
        super().__init__(unit)
        self.identity = InverterIdentity(unit)
        self.telemetry = InverterTelemetry(unit)
        self.grid_meter: GridMeter | None = None
        # Optional blocks; ``_async_setup`` decides which the device serves.
        self.settings: InverterSettings | None = None
        self.battery: Luna2000Telemetry | None = None
        self.battery_overview: Luna2000Overview | None = None
        self.battery_status: Luna2000Status | None = None
        self.battery_settings: Luna2000Settings | None = None
        self.battery_forced: Luna2000ForcedSettings | None = None
        self.battery_peak_shaving: Luna2000PeakShaving | None = None

    @property
    def battery_present(self) -> bool:
        """Whether the device answered the battery telemetry block."""
        return self.battery is not None

    async def _async_setup(self) -> None:
        """Read what never changes and settle which optional blocks exist."""
        self.modbus_unit.require_timeout(REQUIRED_TIMEOUT)

        # Identity first: a failure here means the link is not usable, and the
        # coordinator turns it into ConfigEntryNotReady.
        await self.identity.async_update()

        # The active-power limit register is not served by every firmware.
        self.settings = await read_optional(InverterSettings(self.modbus_unit))

        # An external grid meter is optional; without one no meter entities exist.
        self.grid_meter = await read_optional(GridMeter(self.modbus_unit))

        # The battery telemetry block doubles as the presence probe. Only a
        # device that answers it gets its other battery blocks read.
        self.battery = await read_optional(Luna2000Telemetry(self.modbus_unit))
        if self.battery is None:
            return

        self.battery_overview = await read_optional(Luna2000Overview(self.modbus_unit))
        self.battery_status = await read_optional(Luna2000Status(self.modbus_unit))
        self.battery_settings = await read_optional(Luna2000Settings(self.modbus_unit))
        self.battery_forced = await read_optional(
            Luna2000ForcedSettings(self.modbus_unit)
        )
        self.battery_peak_shaving = await read_optional(
            Luna2000PeakShaving(self.modbus_unit)
        )

    async def async_update(self) -> UpdateReport:
        """Refresh every sub-system this device serves."""
        return await self.async_poll(UPDATE_BLOCKS)

    async def async_read_raw(self, names: Iterable[str] = ALL) -> Raw:
        """Return the raw register map, undecoded, for diagnostics."""
        return await super().async_read_raw(names)
