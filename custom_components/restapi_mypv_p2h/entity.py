"""Base entity for myPV ELWA2."""
from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import MypvP2hCoordinator


class MypvP2hEntity(CoordinatorEntity[MypvP2hCoordinator]):
    """Base entity for ELWA2."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: MypvP2hCoordinator, entry_id: str) -> None:
        super().__init__(coordinator)
        self._entry_id = entry_id

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry_id)},
            name="myPV ELWA2",
            manufacturer="myPV",
            model="ELWA2",
            configuration_url=f"http://{self.coordinator.host}",
        )
