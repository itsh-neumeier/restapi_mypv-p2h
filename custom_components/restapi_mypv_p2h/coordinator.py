"""DataUpdateCoordinator for myPV ELWA2."""
from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

import aiohttp

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

KEEPALIVE_INTERVAL = timedelta(seconds=5)


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
        self._target_power: int = 0
        self._keepalive_unsub: Any = None

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
        """Send power setpoint and manage keepalive."""
        self._target_power = power
        await self._send_power(power)
        self._update_keepalive()

    async def _send_power(self, power: int) -> None:
        url = f"http://{self.host}/control.html?power={power}"
        try:
            async with self._session.get(
                url, timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                resp.raise_for_status()
        except Exception as err:
            _LOGGER.error("Failed to set power: %s", err)

    def _update_keepalive(self) -> None:
        """Start keepalive when power > 0, cancel when power == 0."""
        if self._keepalive_unsub:
            self._keepalive_unsub()
            self._keepalive_unsub = None
        if self._target_power > 0:
            self._keepalive_unsub = async_track_time_interval(
                self.hass, self._async_keepalive, KEEPALIVE_INTERVAL
            )

    async def _async_keepalive(self, _now: Any = None) -> None:
        if self._target_power > 0:
            await self._send_power(self._target_power)

    def cancel_keepalive(self) -> None:
        """Cancel keepalive on integration unload."""
        if self._keepalive_unsub:
            self._keepalive_unsub()
            self._keepalive_unsub = None
