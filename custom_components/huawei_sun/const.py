"""Constants for the Huawei SUN2000 integration."""

from __future__ import annotations

from logging import Logger, getLogger
from typing import Final

LOGGER: Logger = getLogger(__package__)

DOMAIN: Final = "huawei_sun"

DEFAULT_PORT: Final = 8899
DEFAULT_UNIT_ID: Final = 1

CONF_UNIT_ID: Final = "unit_id"
CONF_SCAN_INTERVAL: Final = "scan_interval"

DEFAULT_SCAN_INTERVAL: Final = 30
MIN_SCAN_INTERVAL: Final = 5
MAX_SCAN_INTERVAL: Final = 3600

#: The inverter can take several seconds to answer; keep the config form from
#: hanging on an unreachable host.
CONNECT_TIMEOUT: Final = 30

#: A link that stays up but goes silent is disconnected after this many
#: timeouts in a row, so the next poll opens a fresh one.
TIMEOUTS_BEFORE_DISCONNECT: Final = 3
