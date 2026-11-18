"""Custom types for the Huawei SUN2000 integration."""

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry

    from .coordinator import HuaweiSunCoordinator

type HuaweiSunConfigEntry = ConfigEntry[HuaweiSunData]


@dataclass
class HuaweiSunData:
    """Runtime data held by a loaded config entry."""

    coordinator: HuaweiSunCoordinator
