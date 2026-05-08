"""Config flow for myPV ELWA2."""
from __future__ import annotations

import aiohttp
import voluptuous as vol

from homeassistant.config_entries import ConfigEntry, ConfigFlow, OptionsFlow
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    CONF_HOST,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    MAX_SCAN_INTERVAL,
    MIN_SCAN_INTERVAL,
)


class MypvP2hConfigFlow(ConfigFlow, domain=DOMAIN):
    """Config flow for myPV ELWA2."""

    VERSION = 1

    async def async_step_user(self, user_input: dict | None = None) -> FlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            host = user_input[CONF_HOST]
            await self.async_set_unique_id(host)
            self._abort_if_unique_id_configured()

            if await self._test_connection(host):
                return self.async_create_entry(
                    title=f"myPV ELWA2 ({host})",
                    data=user_input,
                )
            errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST): str,
                    vol.Optional(
                        CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL
                    ): vol.All(
                        int, vol.Range(min=MIN_SCAN_INTERVAL, max=MAX_SCAN_INTERVAL)
                    ),
                }
            ),
            errors=errors,
        )

    async def _test_connection(self, host: str) -> bool:
        url = f"http://{host}/data.jsn"
        session = async_get_clientsession(self.hass)
        try:
            async with session.get(
                url, timeout=aiohttp.ClientTimeout(total=5)
            ) as resp:
                if resp.status != 200:
                    return False
                await resp.json(content_type=None)
                return True
        except Exception:
            return False

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> MypvP2hOptionsFlow:
        return MypvP2hOptionsFlow()


class MypvP2hOptionsFlow(OptionsFlow):
    """Options flow for myPV ELWA2."""

    async def async_step_init(self, user_input: dict | None = None) -> FlowResult:
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current = self.config_entry.options.get(
            CONF_SCAN_INTERVAL,
            self.config_entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
        )

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(CONF_SCAN_INTERVAL, default=current): vol.All(
                        int, vol.Range(min=MIN_SCAN_INTERVAL, max=MAX_SCAN_INTERVAL)
                    ),
                }
            ),
        )
