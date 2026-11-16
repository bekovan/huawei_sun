"""Base entity for the Huawei SUN2000 integration."""

from __future__ import annotations

from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import HuaweiSunCoordinator


class HuaweiSunEntity(CoordinatorEntity[HuaweiSunCoordinator]):
    """Common behaviour for every entity of this integration."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: HuaweiSunCoordinator) -> None:
        """Bind the entity to its coordinator and device."""
        super().__init__(coordinator)
        self._attr_device_info = coordinator.device_info

    @property
    def available(self) -> bool:
        """Go unavailable when the block this entity reads failed to refresh."""
        report_name = getattr(self.entity_description, "report_name", None)
        if report_name is None:
            return super().available
        return super().available and report_name in self.coordinator.data.updated
