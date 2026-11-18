"""Async Open-Meteo client (aiohttp)."""

from __future__ import annotations

from types import TracebackType
from typing import Any, Self

import aiohttp

from . import const as c
from .exceptions import (
    OpenMeteoConnectionError,
    OpenMeteoInvalidLocationError,
    OpenMeteoParseError,
    OpenMeteoRateLimitError,
    OpenMeteoRequestError,
)
from .models import AirQuality, Forecast
from .parser import parse_air_quality, parse_forecast

USER_AGENT = f"aioopenmeteo/{c.__version__} (+https://github.com/briis/aioopenmeteo)"


class OpenMeteoClient:
    """Forecast and air quality for one location.

    Pass Home Assistant's shared session (`async_get_clientsession(hass)`); without
    one the client creates and owns a session (close it with `close()` or
    `async with`).
    """

    def __init__(
        self,
        latitude: float,
        longitude: float,
        *,
        session: aiohttp.ClientSession | None = None,
        model: str = c.DEFAULT_MODEL,
        forecast_days: int = c.DEFAULT_FORECAST_DAYS,
        minutely_15_steps: int = c.DEFAULT_MINUTELY_15_STEPS,
        api_key: str | None = None,
        timeout: float = c.DEFAULT_TIMEOUT,
    ) -> None:
        if not -90 <= latitude <= 90 or not -180 <= longitude <= 180:
            raise ValueError(f"Invalid coordinates: {latitude}, {longitude}")
        if not 1 <= forecast_days <= c.MAX_FORECAST_DAYS:
            raise ValueError(f"forecast_days must be 1-{c.MAX_FORECAST_DAYS}")
        self.latitude = latitude
        self.longitude = longitude
        self.model = model or c.DEFAULT_MODEL
        self.forecast_days = forecast_days
        self.minutely_15_steps = minutely_15_steps
        self.api_key = api_key or None
        self.timeout = timeout
        self._session = session
        self._own_session = session is None

    # -- requests ---------------------------------------------------------------

    def _base_params(self) -> dict[str, str]:
        params = {
            "latitude": f"{self.latitude:.4f}",
            "longitude": f"{self.longitude:.4f}",
            "timezone": "auto",
            "timeformat": "unixtime",
        }
        if self.api_key:
            params["apikey"] = self.api_key
        return params

    def forecast_params(
        self,
        *,
        current: bool = True,
        hourly: bool = True,
        daily: bool = True,
        minutely_15: bool = True,
    ) -> dict[str, str]:
        """Query parameters for the forecast request (exposed for debugging)."""
        params = self._base_params()
        params["models"] = self.model
        params["forecast_days"] = str(self.forecast_days)
        if current:
            params["current"] = ",".join(c.CURRENT_VARIABLES)
        if hourly:
            params["hourly"] = ",".join(c.HOURLY_VARIABLES)
        if daily:
            params["daily"] = ",".join(c.DAILY_VARIABLES)
        if minutely_15 and self.minutely_15_steps > 0:
            params["minutely_15"] = ",".join(c.MINUTELY_15_VARIABLES)
            params["forecast_minutely_15"] = str(self.minutely_15_steps)
        return params

    def air_quality_params(self) -> dict[str, str]:
        params = self._base_params()
        params["current"] = ",".join(c.AIR_QUALITY_CURRENT_VARIABLES)
        params["hourly"] = ",".join(c.AIR_QUALITY_HOURLY_VARIABLES)
        params["forecast_days"] = str(c.DEFAULT_AIR_QUALITY_FORECAST_DAYS)
        params["domains"] = "auto"
        return params

    async def _request(self, url: str, params: dict[str, str]) -> Any:
        if self._session is None:
            self._session = aiohttp.ClientSession()
        try:
            async with self._session.get(
                url,
                params=params,
                headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
                timeout=aiohttp.ClientTimeout(total=self.timeout),
            ) as resp:
                if resp.status >= 400:
                    await self._raise_for_status(resp)
                try:
                    return await resp.json(content_type=None)
                except ValueError as err:
                    raise OpenMeteoParseError(f"Invalid JSON from Open-Meteo: {err}") from err
        except (aiohttp.ClientError, TimeoutError) as err:
            raise OpenMeteoConnectionError(f"Error talking to Open-Meteo: {err!r}") from err

    @staticmethod
    async def _raise_for_status(resp: aiohttp.ClientResponse) -> None:
        text = await resp.text()
        reason = text
        try:
            body = await resp.json(content_type=None)
            if isinstance(body, dict) and body.get("reason"):
                reason = str(body["reason"])
        except ValueError:
            pass
        if resp.status == 429:
            retry_after: float | None = None
            header = resp.headers.get("Retry-After")
            if header:
                try:
                    retry_after = float(header)
                except ValueError:
                    retry_after = None
            raise OpenMeteoRateLimitError(reason, retry_after)
        if resp.status == 400 and "no data is available" in reason.lower():
            raise OpenMeteoInvalidLocationError(resp.status, reason)
        raise OpenMeteoRequestError(resp.status, reason)

    def _url(self, free: str, commercial: str) -> str:
        return commercial if self.api_key else free

    async def get_forecast(self, *, minutely_15: bool = True) -> Forecast:
        """Current conditions, hourly, daily and (optionally) 15-minute forecast."""
        data = await self._request(
            self._url(c.FORECAST_URL, c.COMMERCIAL_FORECAST_URL),
            self.forecast_params(minutely_15=minutely_15),
        )
        return parse_forecast(data, self.model)

    async def get_air_quality(self) -> AirQuality:
        """Current air quality and pollen (CAMS), with a 2 day hourly forecast."""
        data = await self._request(
            self._url(c.AIR_QUALITY_URL, c.COMMERCIAL_AIR_QUALITY_URL),
            self.air_quality_params(),
        )
        return parse_air_quality(data)

    # -- session ----------------------------------------------------------------

    async def close(self) -> None:
        if self._own_session and self._session is not None:
            await self._session.close()
            self._session = None

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        await self.close()
