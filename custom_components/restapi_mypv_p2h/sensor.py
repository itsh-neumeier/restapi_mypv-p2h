"""Sensors for myPV ELWA2."""
from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory, UnitOfEnergy, UnitOfPower, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, ELWA2_DATA_KEYS
from .coordinator import MypvP2hCoordinator
from .entity import MypvP2hEntity


@dataclass(frozen=True, kw_only=True)
class MypvP2hSensorDescription(SensorEntityDescription):
    """Extended sensor description."""

    data_key: str


SENSORS: tuple[MypvP2hSensorDescription, ...] = (
    MypvP2hSensorDescription(
        key="power_setpoint",
        data_key=ELWA2_DATA_KEYS["power"],
        translation_key="power_setpoint",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    MypvP2hSensorDescription(
        key="temperature_1",
        data_key=ELWA2_DATA_KEYS["temp1"],
        translation_key="temperature_1",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    MypvP2hSensorDescription(
        key="temperature_2",
        data_key=ELWA2_DATA_KEYS["temp2"],
        translation_key="temperature_2",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    MypvP2hSensorDescription(
        key="energy_today",
        data_key=ELWA2_DATA_KEYS["energy"],
        translation_key="energy_today",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: MypvP2hCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        MypvP2hSensor(coordinator, entry.entry_id, desc) for desc in SENSORS
    )


class MypvP2hSensor(MypvP2hEntity, SensorEntity):
    """ELWA2 sensor."""

    entity_description: MypvP2hSensorDescription

    def __init__(
        self,
        coordinator: MypvP2hCoordinator,
        entry_id: str,
        description: MypvP2hSensorDescription,
    ) -> None:
        super().__init__(coordinator, entry_id)
        self.entity_description = description
        self._attr_unique_id = f"{entry_id}_{description.key}"

    @property
    def native_value(self) -> float | int | None:
        return self.coordinator.data.get(self.entity_description.data_key)

    @property
    def available(self) -> bool:
        if not super().available:
            return False
        if self.entity_description.key == "temperature_2":
            return self.coordinator.data.get(self.entity_description.data_key) is not None
        return True
