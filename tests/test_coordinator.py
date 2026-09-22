"""Tests for the myPV P2H DataUpdateCoordinator."""
from __future__ import annotations

import aiohttp

from custom_components.restapi_mypv_p2h.coordinator import MypvP2hCoordinator

VALID_DATA = {"power_elwa2": 500, "temp1": 450}
DATA_URL = "http://1.2.3.4/data.jsn"


async def test_update_success(hass, aioclient_mock):
    """A valid JSON response populates coordinator.data."""
    aioclient_mock.get(DATA_URL, json=VALID_DATA)
    coordinator = MypvP2hCoordinator(hass, "1.2.3.4", 30)

    await coordinator.async_refresh()

    assert coordinator.last_update_success
    assert coordinator.data == VALID_DATA


async def test_update_timeout(hass, aioclient_mock):
    """A request timeout results in a failed (not crashed) update."""
    aioclient_mock.get(DATA_URL, exc=TimeoutError())
    coordinator = MypvP2hCoordinator(hass, "1.2.3.4", 30)

    await coordinator.async_refresh()

    assert not coordinator.last_update_success


async def test_update_http_error(hass, aioclient_mock):
    """A non-2xx HTTP status results in a failed update."""
    aioclient_mock.get(DATA_URL, status=500)
    coordinator = MypvP2hCoordinator(hass, "1.2.3.4", 30)

    await coordinator.async_refresh()

    assert not coordinator.last_update_success


async def test_update_malformed_json(hass, aioclient_mock):
    """A response that is not valid JSON results in a failed update."""
    aioclient_mock.get(DATA_URL, text="this is not json")
    coordinator = MypvP2hCoordinator(hass, "1.2.3.4", 30)

    await coordinator.async_refresh()

    assert not coordinator.last_update_success


async def test_update_unreachable(hass, aioclient_mock):
    """Connection refused / host unreachable results in a failed update."""
    aioclient_mock.get(DATA_URL, exc=aiohttp.ClientConnectionError())
    coordinator = MypvP2hCoordinator(hass, "1.2.3.4", 30)

    await coordinator.async_refresh()

    assert not coordinator.last_update_success


async def test_recovery_after_failure(hass, aioclient_mock):
    """The coordinator recovers once communication returns."""
    aioclient_mock.get(DATA_URL, exc=aiohttp.ClientConnectionError())
    coordinator = MypvP2hCoordinator(hass, "1.2.3.4", 30)

    await coordinator.async_refresh()
    assert not coordinator.last_update_success

    aioclient_mock.clear_requests()
    aioclient_mock.get(DATA_URL, json=VALID_DATA)

    await coordinator.async_refresh()
    assert coordinator.last_update_success
    assert coordinator.data == VALID_DATA
