from __future__ import annotations

import asyncio
from aiohttp import ClientSession


class WatercoolerApiError(Exception):
    """API 访问失败。"""


class WatercoolerApiClient:
    def __init__(self, session: ClientSession, host: str, port: int) -> None:
        self._session = session
        self._host = host.strip().removeprefix("http://").removeprefix("https://").strip("/")
        self._port = int(port)

    @property
    def base_url(self) -> str:
        return f"http://{self._host}:{self._port}"

    async def async_get_status(self) -> dict:
        url = f"{self.base_url}/api/status"
        try:
            async with asyncio.timeout(8):
                resp = await self._session.get(url)
                data = await resp.json(content_type=None)
        except Exception as exc:  # noqa: BLE001
            raise WatercoolerApiError(str(exc)) from exc
        if resp.status >= 400:
            raise WatercoolerApiError(f"HTTP {resp.status}")
        if not isinstance(data, dict) or not data.get("ok", False):
            raise WatercoolerApiError("invalid api payload")
        return data
