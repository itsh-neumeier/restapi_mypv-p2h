"""Base entity for myPV P2H."""
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
        data = self.coordinator.data or {}
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry_id)},
            name="myPV P2H",
            manufacturer="my-PV GmbH",
            model="AC ELWA 2",
            sw_version=data.get("fwversion"),
            configuration_url=f"http://{self.coordinator.host}/control.html",
        )
