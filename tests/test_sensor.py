"""Tests for myPV P2H sensors."""
from __future__ import annotations

import aiohttp
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.restapi_mypv_p2h.const import CONF_HOST, CONF_SCAN_INTERVAL, DOMAIN

DATA_URL = "http://1.2.3.4/data.jsn"


async def _setup_entry(hass, aioclient_mock, data: dict) -> MockConfigEntry:
    aioclient_mock.get(DATA_URL, json=data)
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_HOST: "1.2.3.4", CONF_SCAN_INTERVAL: 30},
        unique_id="1.2.3.4",
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    return entry


def _entity_id(hass, entry: MockConfigEntry, key: str) -> str:
    registry = er.async_get(hass)
    entity_id = registry.async_get_entity_id("sensor", DOMAIN, f"{entry.entry_id}_{key}")
    assert entity_id is not None, f"no entity registered for key {key}"
    return entity_id


async def test_value_conversion_power_setpoint(hass, aioclient_mock):
    """power_setpoint passes the raw watt value through unscaled."""
    entry = await _setup_entry(hass, aioclient_mock, {"power_elwa2": 750, "temp1": 400})

    assert hass.states.get(_entity_id(hass, entry, "power_setpoint")).state == "750"


async def test_scaling_temperature(hass, aioclient_mock):
    """temp1 is scaled by 0.1 (device sends tenths of a degree)."""
    entry = await _setup_entry(hass, aioclient_mock, {"power_elwa2": 0, "temp1": 456})

    assert hass.states.get(_entity_id(hass, entry, "temperature_1")).state == "45.6"


async def test_scaling_frequency(hass, aioclient_mock):
    """freq is scaled by 0.001 (device sends mHz)."""
    entry = await _setup_entry(
        hass, aioclient_mock, {"power_elwa2": 0, "temp1": 0, "freq": 50123}
    )

    assert hass.states.get(_entity_id(hass, entry, "freq")).state == "50.1"


async def test_optional_field_missing_is_unavailable(hass, aioclient_mock):
    """temperature_2 is optional; without the key the sensor is unavailable."""
    entry = await _setup_entry(hass, aioclient_mock, {"power_elwa2": 0, "temp1": 0})

    assert hass.states.get(_entity_id(hass, entry, "temperature_2")).state == "unavailable"


async def test_optional_field_present_is_available(hass, aioclient_mock):
    """Once the firmware reports temp2, the optional sensor becomes available."""
    entry = await _setup_entry(
        hass, aioclient_mock, {"power_elwa2": 0, "temp1": 0, "temp2": 300}
    )

    assert hass.states.get(_entity_id(hass, entry, "temperature_2")).state == "30.0"


async def test_enum_known_value(hass, aioclient_mock):
    """A documented warning code maps to its translation key."""
    entry = await _setup_entry(
        hass, aioclient_mock, {"power_elwa2": 0, "temp1": 0, "warnings": 202}
    )

    assert hass.states.get(_entity_id(hass, entry, "warnings")).state == "overtemp"


async def test_enum_unknown_value_falls_back_without_crashing(hass, aioclient_mock):
    """An unknown/future warning code must not crash the sensor.

    HA's ENUM sensors require `state` to be one of the declared `options`, so
    the raw code cannot be used as the state directly; it must still be
    recoverable, which we do via the raw_value attribute.
    """
    entry = await _setup_entry(
        hass, aioclient_mock, {"power_elwa2": 0, "temp1": 0, "warnings": 999}
    )

    state = hass.states.get(_entity_id(hass, entry, "warnings"))
    assert state.state == "unknown"
    assert state.attributes["raw_value"] == 999


async def test_sensor_unavailable_when_coordinator_update_fails(hass, aioclient_mock):
    """A non-optional sensor still goes unavailable when polling fails outright."""
    entry = await _setup_entry(hass, aioclient_mock, {"power_elwa2": 0, "temp1": 0})
    entity_id = _entity_id(hass, entry, "power_setpoint")
    assert hass.states.get(entity_id).state != "unavailable"

    coordinator = hass.data[DOMAIN][entry.entry_id]
    aioclient_mock.clear_requests()
    aioclient_mock.get(DATA_URL, exc=aiohttp.ClientConnectionError())
    await coordinator.async_refresh()
    await hass.async_block_till_done()

    assert hass.states.get(entity_id).state == "unavailable"
