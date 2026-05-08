"""Number entity for myPV P2H."""
from __future__ import annotations

import logging

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfPower
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import MypvP2hCoordinator
from .entity import MypvP2hEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: MypvP2hCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([MypvP2hPowerNumber(coordinator, entry.entry_id)])


class MypvP2hPowerNumber(MypvP2hEntity, NumberEntity):
    """ELWA2 power setpoint number."""

    _attr_translation_key = "target_power"
    _attr_native_min_value = 0
    _attr_native_max_value = 3500
    _attr_native_step = 50
    _attr_mode = NumberMode.SLIDER
    _attr_native_unit_of_measurement = UnitOfPower.WATT

    def __init__(self, coordinator: MypvP2hCoordinator, entry_id: str) -> None:
        super().__init__(coordinator, entry_id)
        self._attr_unique_id = f"{entry_id}_target_power"

    @property
    def native_value(self) -> float | None:
        return self.coordinator.data.get("power")

    async def async_set_native_value(self, value: float) -> None:
        await self.coordinator.async_set_power(int(value))
        await self.coordinator.async_request_refresh()
