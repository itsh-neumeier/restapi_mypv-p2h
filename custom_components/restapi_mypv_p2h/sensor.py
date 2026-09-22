"""Sensors for myPV P2H."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from homeassistant.components.sensor import (
    RestoreSensor,
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    EntityCategory,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfFrequency,
    UnitOfPower,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt as dt_util

from .const import DOMAIN, ELWA2_DATA_KEYS
from .coordinator import MypvP2hCoordinator
from .entity import MypvP2hEntity

# HA's ENUM sensor state must be one of `options`; any code not present in a
# value_map below falls back to this instead of the raw code (see native_value).
UNKNOWN_ENUM_VALUE = "unknown"

UPD_STATE_MAP: dict[int, str] = {
    0: "no_update",
    1: "available",
    3: "downloading",
    5: "interrupted",
    10: "ready",
}

WARNINGS_MAP: dict[int, str] = {
    0: "ok",
    201: "stl_triggered",
    202: "overtemp",
    203: "temp_probe_fault",
    204: "hardware_fault",
    205: "temp_sensor_fault",
    209: "mainboard_error",
}


@dataclass(frozen=True, kw_only=True)
class MypvP2hSensorDescription(SensorEntityDescription):
    """Extended sensor description."""

    data_key: str
    scale: float = 1.0
    optional: bool = False
    value_map: dict[int, str] | None = field(default=None, compare=False)


SENSORS: tuple[MypvP2hSensorDescription, ...] = (
    MypvP2hSensorDescription(
        key="power_setpoint",
        data_key=ELWA2_DATA_KEYS["power"],
        translation_key="power_setpoint",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
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
    MypvP2hSensorDescription(
        key="upd_state",
        data_key=ELWA2_DATA_KEYS["upd_state"],
        translation_key="upd_state",
        device_class=SensorDeviceClass.ENUM,
        entity_category=EntityCategory.DIAGNOSTIC,
        options=[*UPD_STATE_MAP.values(), UNKNOWN_ENUM_VALUE],
        value_map=UPD_STATE_MAP,
        optional=True,
    ),
    MypvP2hSensorDescription(
        key="warnings",
        data_key=ELWA2_DATA_KEYS["warnings"],
        translation_key="warnings",
        device_class=SensorDeviceClass.ENUM,
        entity_category=EntityCategory.DIAGNOSTIC,
        options=[*WARNINGS_MAP.values(), UNKNOWN_ENUM_VALUE],
        value_map=WARNINGS_MAP,
        optional=True,
    ),
    MypvP2hSensorDescription(
        key="cur_ip",
        data_key=ELWA2_DATA_KEYS["cur_ip"],
        translation_key="cur_ip",
        entity_category=EntityCategory.DIAGNOSTIC,
        optional=True,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: MypvP2hCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities: list[SensorEntity] = [
        MypvP2hSensor(coordinator, entry.entry_id, desc) for desc in SENSORS
    ]
    entities.append(MypvP2hEnergySensor(coordinator, entry.entry_id))
    async_add_entities(entities)


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
        if self.entity_description.value_map is not None:
            # `options` only lists known codes; an unmapped code must fall back
            # to UNKNOWN_ENUM_VALUE (not the raw code) or HA's ENUM validation
            # raises and the entity fails to add. The raw code is still
            # available via the raw_value state attribute below.
            return self.entity_description.value_map.get(int(value), UNKNOWN_ENUM_VALUE)
        if self.entity_description.scale != 1.0:
            return round(value * self.entity_description.scale, 1)
        return value

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        if self.entity_description.value_map is None:
            return None
        value = self.coordinator.data.get(self.entity_description.data_key)
        if value is None:
            return None
        return {"raw_value": value}

    @property
    def available(self) -> bool:
        if not super().available:
            return False
        if self.entity_description.optional:
            return self.coordinator.data.get(self.entity_description.data_key) is not None
        return True


class MypvP2hEnergySensor(MypvP2hEntity, RestoreSensor):
    """Energy consumption, integrated from the measured power.

    The device API exposes only instantaneous power (power_elwa2), no
    cumulative energy counter (see CHANGELOG: the old `energy_today` sensor
    was removed because that field does not exist). This sensor integrates
    measured power over real elapsed time (left Riemann sum) into kWh, so it
    can be used as an "individual device" source in the HA Energy Dashboard,
    which only accepts device_class ENERGY / state_class TOTAL_INCREASING
    sensors. The running total survives HA restarts via RestoreSensor.
    """

    _attr_translation_key = "energy_consumption"
    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
    _attr_suggested_display_precision = 2

    def __init__(self, coordinator: MypvP2hCoordinator, entry_id: str) -> None:
        super().__init__(coordinator, entry_id)
        self._attr_unique_id = f"{entry_id}_energy_consumption"
        self._energy_kwh: float = 0.0
        self._last_update: datetime | None = None

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        last_data = await self.async_get_last_sensor_data()
        if last_data is not None and last_data.native_value is not None:
            self._energy_kwh = float(last_data.native_value)
        # Establish the integration baseline from the data already fetched by
        # the coordinator's first refresh; otherwise nothing is integrated
        # until a second coordinator update arrives after this entity exists.
        if (
            self.coordinator.last_update_success
            and self.coordinator.data.get(ELWA2_DATA_KEYS["power"]) is not None
        ):
            self._last_update = dt_util.utcnow()

    def _handle_coordinator_update(self) -> None:
        now = dt_util.utcnow()
        power = (
            self.coordinator.data.get(ELWA2_DATA_KEYS["power"])
            if self.coordinator.last_update_success
            else None
        )
        # No timestamp gap tracked across an outage: a missing/failed read
        # resets `_last_update` to None so the next successful read doesn't
        # integrate power across the unmeasured gap.
        if power is not None and self._last_update is not None:
            hours = (now - self._last_update).total_seconds() / 3600
            self._energy_kwh += max(power, 0) * hours / 1000
        self._last_update = now if power is not None else None
        self.async_write_ha_state()

    @property
    def native_value(self) -> float:
        return round(self._energy_kwh, 3)

    @property
    def available(self) -> bool:
        if not super().available:
            return False
        return self.coordinator.data.get(ELWA2_DATA_KEYS["power"]) is not None
