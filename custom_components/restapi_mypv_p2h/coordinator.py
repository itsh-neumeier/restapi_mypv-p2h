"""DataUpdateCoordinator for myPV ELWA2."""
from __future__ import annotations

import logging
from datetime import timedelta

import aiohttp

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class MypvP2hCoordinator(DataUpdateCoordinator[dict]):
    """Coordinator for myPV ELWA2."""

    def __init__(self, hass: HomeAssistant, host: str, scan_interval: int) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
        )
        self.host = host
        self._session = async_get_clientsession(hass)

    async def _async_update_data(self) -> dict:
        url = f"http://{self.host}/data.jsn"
        try:
            async with self._session.get(
                url, timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                resp.raise_for_status()
                return await resp.json(content_type=None)
        except Exception as err:
            raise UpdateFailed(f"Error communicating with ELWA2: {err}") from err

    async def async_set_power(self, power: int) -> None:
        """Send power setpoint to device."""
        url = f"http://{self.host}/control.html?power={power}"
        try:
            async with self._session.get(
                url, timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                resp.raise_for_status()
        except Exception as err:
            _LOGGER.error("Failed to set power: %s", err)
