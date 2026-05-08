"""Binary sensors for myPV P2H."""
from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, ELWA2_DATA_KEYS, STATUS_ERROR
from .coordinator import MypvP2hCoordinator
from .entity import MypvP2hEntity


@dataclass(frozen=True, kw_only=True)
class MypvP2hBinarySensorDescription(BinarySensorEntityDescription):
    """Extended binary sensor description."""

    data_key: str
    on_value: int = 1


BINARY_SENSORS: tuple[MypvP2hBinarySensorDescription, ...] = (
    MypvP2hBinarySensorDescription(
        key="boost_active",
        data_key=ELWA2_DATA_KEYS["boost"],
        translation_key="boost_active",
        entity_category=EntityCategory.DIAGNOSTIC,
        on_value=1,
    ),
    MypvP2hBinarySensorDescription(
        key="error",
        data_key=ELWA2_DATA_KEYS["status"],
        translation_key="error",
        device_class=BinarySensorDeviceClass.PROBLEM,
        entity_category=EntityCategory.DIAGNOSTIC,
        on_value=STATUS_ERROR,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: MypvP2hCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        MypvP2hBinarySensor(coordinator, entry.entry_id, desc) for desc in BINARY_SENSORS
    )


class MypvP2hBinarySensor(MypvP2hEntity, BinarySensorEntity):
    """ELWA2 binary sensor."""

    entity_description: MypvP2hBinarySensorDescription

    def __init__(
        self,
        coordinator: MypvP2hCoordinator,
        entry_id: str,
        description: MypvP2hBinarySensorDescription,
    ) -> None:
        super().__init__(coordinator, entry_id)
        self.entity_description = description
        self._attr_unique_id = f"{entry_id}_{description.key}"

    @property
    def is_on(self) -> bool | None:
        value = self.coordinator.data.get(self.entity_description.data_key)
        if value is None:
            return None
        return value == self.entity_description.on_value
