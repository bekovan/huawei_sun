"""
Named values and status maps reported by Huawei inverters.

The numeric values come from the Huawei SUN2000 Modbus interface definition and
were cross-checked against the community ``huawei-solar`` register list. Only
values this integration displays are kept here; everything else is exposed as a
plain register value.
"""

from collections.abc import Mapping
from typing import Final

#: Inverter running state (register 32089).
DEVICE_STATUS: Final[Mapping[int, str]] = {
    0x0000: "Standby: initializing",
    0x0001: "Standby: detecting insulation resistance",
    0x0002: "Standby: detecting irradiation",
    0x0003: "Standby: grid detecting",
    0x0100: "Starting",
    0x0200: "On-grid",
    0x0201: "On-grid: power limited",
    0x0202: "On-grid: self-derating",
    0x0203: "Off-grid running",
    0x0300: "Shutdown: fault",
    0x0301: "Shutdown: command",
    0x0302: "Shutdown: OVGR",
    0x0303: "Shutdown: communication disconnected",
    0x0304: "Shutdown: power limited",
    0x0305: "Shutdown: manual startup required",
    0x0306: "Shutdown: DC switches disconnected",
    0x0307: "Shutdown: rapid cutoff",
    0x0308: "Shutdown: input underpowered",
    0x030C: "Shutdown: battery end-of-discharge",
    0x0401: "Grid scheduling: cosphi-P curve",
    0x0402: "Grid scheduling: Q-U curve",
    0x0403: "Grid scheduling: PF-U curve",
    0x0404: "Grid scheduling: dry contact",
    0x0405: "Grid scheduling: Q-P curve",
    0x0500: "Spot-check ready",
    0x0501: "Spot-checking",
    0x0600: "Inspecting",
    0x0700: "AFCI self check",
    0x0800: "I-V scanning",
    0x0900: "DC input detection",
    0x0A00: "Off-grid charging",
    0xA000: "Standby: no irradiation",
}

#: LUNA2000 unit running state (register 37000).
STORAGE_STATUS: Final[Mapping[int, str]] = {
    0: "Offline",
    1: "Standby",
    2: "Running",
    3: "Fault",
    4: "Sleep mode",
}

#: LUNA2000 working mode as reported by the inverter (register 37006).
STORAGE_WORKING_MODE_B: Final[Mapping[int, str]] = {
    0: "None",
    1: "Forcible charge/discharge",
    2: "Time of use (LG)",
    3: "Fixed charge/discharge",
    4: "Maximise self-consumption",
    5: "Fully fed to grid",
    6: "Time of use (LUNA2000)",
    7: "Remote scheduling: maximum self-use",
    8: "Remote scheduling: full grid feed-in",
    9: "Remote scheduling: time of use",
    10: "AI energy management and scheduling",
    11: "Remote scheduling: AI control",
}

#: LUNA2000 working mode that can be written (register 47086).
STORAGE_WORKING_MODE: Final[Mapping[int, str]] = {
    0: "Adaptive",
    1: "Fixed charge/discharge",
    2: "Maximise self-consumption",
    3: "Time of use (LG)",
    4: "Fully fed to grid",
    5: "Time of use (LUNA2000)",
    6: "Third-party control",
}

#: Forced charge/discharge action (register 47100).
FORCIBLE_CHARGE_DISCHARGE: Final[Mapping[int, str]] = {
    0: "Stop",
    1: "Charge",
    2: "Discharge",
}

#: How a forced charge/discharge ends (register 47246).
FORCIBLE_TARGET_MODE: Final[Mapping[int, str]] = {
    0: "Time",
    1: "State of charge",
}

#: LUNA2000 unit connection state (register 37994).
STORAGE_CONNECT_STATUS: Final[Mapping[int, str]] = {
    32764: "Connected",
    32765: "Connecting",
    45056: "Offline",
    45057: "Online",
}

#: Values that mean the battery unit is reachable.
STORAGE_CONNECTED_VALUES: Final[frozenset[int]] = frozenset({32764, 45057})


def label(mapping: Mapping[int, str], value: int | None) -> str | None:
    """
    Return the human-readable label for a register value.

    Unknown values are shown as ``Unknown (<value>)`` instead of being hidden,
    so a firmware update that adds a state is visible rather than silently
    turning an entity into ``unknown``.
    """
    if value is None:
        return None
    return mapping.get(value, f"Unknown ({value})")
