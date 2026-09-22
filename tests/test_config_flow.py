"""Tests for the myPV P2H config flow."""
from __future__ import annotations

import aiohttp
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.restapi_mypv_p2h.const import CONF_HOST, CONF_SCAN_INTERVAL, DOMAIN

VALID_DATA_JSON = {"power_elwa2": 0, "temp1": 450, "fwversion": "1.0"}
DATA_URL = "http://1.2.3.4/data.jsn"


async def _start_user_flow(hass):
    return await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )


async def test_user_flow_success(hass, aioclient_mock):
    """A reachable device with a valid response creates a config entry."""
    aioclient_mock.get(DATA_URL, json=VALID_DATA_JSON)

    result = await _start_user_flow(hass)
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_HOST: "1.2.3.4", CONF_SCAN_INTERVAL: 30}
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"][CONF_HOST] == "1.2.3.4"


async def test_user_flow_cannot_connect(hass, aioclient_mock):
    """A connection error is surfaced as cannot_connect, not an exception."""
    aioclient_mock.get(DATA_URL, exc=aiohttp.ClientConnectionError())

    result = await _start_user_flow(hass)
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_HOST: "1.2.3.4", CONF_SCAN_INTERVAL: 30}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "cannot_connect"}


async def test_user_flow_invalid_json(hass, aioclient_mock):
    """A malformed (non-JSON) response is also treated as cannot_connect."""
    aioclient_mock.get(DATA_URL, text="not valid json")

    result = await _start_user_flow(hass)
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_HOST: "1.2.3.4", CONF_SCAN_INTERVAL: 30}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "cannot_connect"}


async def test_user_flow_retry_after_failure(hass, aioclient_mock):
    """After a failed attempt, the same flow succeeds once the device answers."""
    aioclient_mock.get(DATA_URL, exc=aiohttp.ClientConnectionError())

    result = await _start_user_flow(hass)
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_HOST: "1.2.3.4", CONF_SCAN_INTERVAL: 30}
    )
    assert result["errors"] == {"base": "cannot_connect"}

    aioclient_mock.clear_requests()
    aioclient_mock.get(DATA_URL, json=VALID_DATA_JSON)

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_HOST: "1.2.3.4", CONF_SCAN_INTERVAL: 30}
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY


async def test_user_flow_duplicate_device(hass, aioclient_mock):
    """The same host cannot be configured twice."""
    aioclient_mock.get(DATA_URL, json=VALID_DATA_JSON)

    entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_HOST: "1.2.3.4", CONF_SCAN_INTERVAL: 30},
        unique_id="1.2.3.4",
    )
    entry.add_to_hass(hass)

    result = await _start_user_flow(hass)
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_HOST: "1.2.3.4", CONF_SCAN_INTERVAL: 30}
    )
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"


async def test_options_flow(hass, aioclient_mock):
    """The scan interval can be changed via the options flow."""
    aioclient_mock.get(DATA_URL, json=VALID_DATA_JSON)

    entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_HOST: "1.2.3.4", CONF_SCAN_INTERVAL: 30},
        unique_id="1.2.3.4",
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert result["type"] is FlowResultType.FORM

    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {CONF_SCAN_INTERVAL: 60}
    )
    await hass.async_block_till_done()
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert entry.options[CONF_SCAN_INTERVAL] == 60
