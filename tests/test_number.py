"""Tests for power control (number entity) and the keepalive lifecycle."""
from __future__ import annotations

from datetime import timedelta

import aiohttp
import pytest
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import entity_registry as er
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
    async_fire_time_changed,
)

from custom_components.restapi_mypv_p2h.const import CONF_HOST, CONF_SCAN_INTERVAL, DOMAIN
from custom_components.restapi_mypv_p2h.coordinator import MypvP2hCoordinator

DATA_URL = "http://1.2.3.4/data.jsn"
VALID_DATA = {"power_elwa2": 0, "temp1": 450}


def _control_url(power: int) -> str:
    return f"http://1.2.3.4/control.html?power={power}"


async def test_set_power_zero_no_keepalive(hass, aioclient_mock):
    """Setting 0 W sends the command but never arms the keepalive."""
    aioclient_mock.get(_control_url(0))
    coordinator = MypvP2hCoordinator(hass, "1.2.3.4", 30)

    await coordinator.async_set_power(0)

    assert coordinator._keepalive_unsub is None
    assert len(aioclient_mock.mock_calls) == 1


async def test_set_power_normal_starts_keepalive(hass, aioclient_mock):
    """A positive setpoint sends the command and arms the keepalive."""
    aioclient_mock.get(_control_url(2000))
    coordinator = MypvP2hCoordinator(hass, "1.2.3.4", 30)

    await coordinator.async_set_power(2000)

    assert coordinator._keepalive_unsub is not None
    assert len(aioclient_mock.mock_calls) == 1
    coordinator.cancel_keepalive()


async def test_set_power_max_3500(hass, aioclient_mock):
    """The documented maximum of 3500 W is accepted and sent as-is."""
    aioclient_mock.get(_control_url(3500))
    coordinator = MypvP2hCoordinator(hass, "1.2.3.4", 30)

    await coordinator.async_set_power(3500)

    assert coordinator._target_power == 3500
    assert len(aioclient_mock.mock_calls) == 1
    coordinator.cancel_keepalive()


async def test_keepalive_resends_periodically(hass, aioclient_mock):
    """Every keepalive tick re-sends the current target power."""
    aioclient_mock.get(_control_url(1500))
    coordinator = MypvP2hCoordinator(hass, "1.2.3.4", 30)
    await coordinator.async_set_power(1500)
    assert len(aioclient_mock.mock_calls) == 1

    async_fire_time_changed(hass, dt_util.utcnow() + timedelta(seconds=5))
    await hass.async_block_till_done()
    assert len(aioclient_mock.mock_calls) == 2

    async_fire_time_changed(hass, dt_util.utcnow() + timedelta(seconds=10))
    await hass.async_block_till_done()
    assert len(aioclient_mock.mock_calls) == 3
    coordinator.cancel_keepalive()


async def test_keepalive_cancelled_when_power_set_to_zero(hass, aioclient_mock):
    """Lowering the target back to 0 W stops further keepalive ticks."""
    aioclient_mock.get(_control_url(1500))
    aioclient_mock.get(_control_url(0))
    coordinator = MypvP2hCoordinator(hass, "1.2.3.4", 30)
    await coordinator.async_set_power(1500)
    assert coordinator._keepalive_unsub is not None

    await coordinator.async_set_power(0)
    assert coordinator._keepalive_unsub is None

    calls_before = len(aioclient_mock.mock_calls)
    async_fire_time_changed(hass, dt_util.utcnow() + timedelta(seconds=5))
    await hass.async_block_till_done()
    assert len(aioclient_mock.mock_calls) == calls_before


async def test_cancel_keepalive_on_unload(hass, aioclient_mock):
    """cancel_keepalive() (called on unload) stops further ticks."""
    aioclient_mock.get(_control_url(1500))
    coordinator = MypvP2hCoordinator(hass, "1.2.3.4", 30)
    await coordinator.async_set_power(1500)
    assert coordinator._keepalive_unsub is not None

    coordinator.cancel_keepalive()
    assert coordinator._keepalive_unsub is None

    calls_before = len(aioclient_mock.mock_calls)
    async_fire_time_changed(hass, dt_util.utcnow() + timedelta(seconds=5))
    await hass.async_block_till_done()
    assert len(aioclient_mock.mock_calls) == calls_before


async def test_command_failure_raises_but_keepalive_still_armed(hass, aioclient_mock):
    """A failed send is reported as an error, but the target is still retried."""
    aioclient_mock.get(_control_url(1000), exc=aiohttp.ClientConnectionError())
    coordinator = MypvP2hCoordinator(hass, "1.2.3.4", 30)

    with pytest.raises(HomeAssistantError):
        await coordinator.async_set_power(1000)

    # Keepalive is still armed so a later recovery keeps trying to reach 1000 W.
    assert coordinator._keepalive_unsub is not None
    assert coordinator._target_power == 1000
    coordinator.cancel_keepalive()


async def test_keepalive_tick_swallows_command_failure(hass, aioclient_mock):
    """A failing keepalive tick must not raise out of the scheduled callback."""
    aioclient_mock.get(_control_url(1000))
    coordinator = MypvP2hCoordinator(hass, "1.2.3.4", 30)
    await coordinator.async_set_power(1000)

    aioclient_mock.clear_requests()
    aioclient_mock.get(_control_url(1000), exc=aiohttp.ClientConnectionError())

    # Must not raise.
    await coordinator._async_keepalive()
    coordinator.cancel_keepalive()


async def test_number_entity_rejects_out_of_range_value(hass, aioclient_mock):
    """HA's own number validation blocks values outside 0-3500 before we send anything."""
    aioclient_mock.get(DATA_URL, json=VALID_DATA)
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_HOST: "1.2.3.4", CONF_SCAN_INTERVAL: 30},
        unique_id="1.2.3.4",
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    registry = er.async_get(hass)
    entity_id = registry.async_get_entity_id("number", DOMAIN, f"{entry.entry_id}_target_power")
    assert entity_id is not None

    # HA's own number.set_value schema/range check rejects this before our
    # code runs; the exact exception type has varied across core versions.
    with pytest.raises((ValueError, HomeAssistantError)):
        await hass.services.async_call(
            "number",
            "set_value",
            {"entity_id": entity_id, "value": 4000},
            blocking=True,
        )

    assert len(aioclient_mock.mock_calls) == 1  # only the initial data.jsn poll
