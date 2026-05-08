"""Sensors for myPV P2H."""
from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    EntityCategory,
    UnitOfElectricPotential,
    UnitOfFrequency,
    UnitOfPower,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, ELWA2_DATA_KEYS
from .coordinator import MypvP2hCoordinator
from .entity import MypvP2hEntity


@dataclass(frozen=True, kw_only=True)
class MypvP2hSensorDescription(SensorEntityDescription):
    """Extended sensor description."""

    data_key: str
    scale: float = 1.0
    optional: bool = False


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
        key="surplus",
        data_key=ELWA2_DATA_KEYS["surplus"],
        translation_key="surplus",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        optional=True,
    ),
    MypvP2hSensorDescription(
        key="temperature_1",
        data_key=ELWA2_DATA_KEYS["temp1"],
        translation_key="temperature_1",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        scale=0.1,
    ),
    MypvP2hSensorDescription(
        key="temperature_2",
        data_key=ELWA2_DATA_KEYS["temp2"],
        translation_key="temperature_2",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        scale=0.1,
        optional=True,
    ),
    MypvP2hSensorDescription(
        key="control_state",
        data_key=ELWA2_DATA_KEYS["ctrlstate"],
        translation_key="control_state",
        entity_category=EntityCategory.DIAGNOSTIC,
        optional=True,
    ),
    MypvP2hSensorDescription(
        key="power_solar",
        data_key=ELWA2_DATA_KEYS["power_solar"],
        translation_key="power_solar",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        optional=True,
    ),
    MypvP2hSensorDescription(
        key="power_grid",
        data_key=ELWA2_DATA_KEYS["power_grid"],
        translation_key="power_grid",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        optional=True,
    ),
    MypvP2hSensorDescription(
        key="volt_mains",
        data_key=ELWA2_DATA_KEYS["volt_mains"],
        translation_key="volt_mains",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        optional=True,
    ),
    MypvP2hSensorDescription(
        key="freq",
        data_key=ELWA2_DATA_KEYS["freq"],
        translation_key="freq",
        native_unit_of_measurement=UnitOfFrequency.HERTZ,
        device_class=SensorDeviceClass.FREQUENCY,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        scale=0.001,
        optional=True,
    ),
    MypvP2hSensorDescription(
        key="temp_ps",
        data_key=ELWA2_DATA_KEYS["temp_ps"],
        translation_key="temp_ps",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        scale=0.1,
        optional=True,
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
    """myPV P2H sensor."""

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
    def native_value(self) -> float | int | str | None:
        value = self.coordinator.data.get(self.entity_description.data_key)
        if value is None:
            return None
        if self.entity_description.scale != 1.0:
            return round(value * self.entity_description.scale, 1)
        return value

    @property
    def available(self) -> bool:
        if not super().available:
            return False
        if self.entity_description.optional:
            return self.coordinator.data.get(self.entity_description.data_key) is not None
        return True
