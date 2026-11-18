"""Base entity for the Huawei SUN2000 integration."""

from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import HuaweiSunCoordinator


class HuaweiSunEntity(CoordinatorEntity[HuaweiSunCoordinator]):
    """Common behaviour for every entity of this integration."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: HuaweiSunCoordinator, component: str = "") -> None:
        """Bind the entity to its coordinator and the device it belongs to."""
        super().__init__(coordinator)
        self._attr_device_info = coordinator.device_info_for(component)

    @property
    def available(self) -> bool:
        """Go unavailable when the block this entity reads failed to refresh."""
        report_name = getattr(self.entity_description, "report_name", None)
        if report_name is None:
            return super().available
        return super().available and report_name in self.coordinator.data.updated
