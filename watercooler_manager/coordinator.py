from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import WatercoolerApiClient, WatercoolerApiError
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class WatercoolerDataUpdateCoordinator(DataUpdateCoordinator[dict]):
    def __init__(self, hass: HomeAssistant, api: WatercoolerApiClient, scan_interval: int) -> None:
        self.api = api
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=max(2, int(scan_interval))),
        )

    async def _async_update_data(self) -> dict:
        try:
            return await self.api.async_get_status()
        except WatercoolerApiError as exc:
            raise UpdateFailed(str(exc)) from exc
