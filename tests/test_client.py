"""Client tests against mocked HTTP."""

from __future__ import annotations

import re

from aioresponses import aioresponses
import pytest

from aioopenmeteo import (
    OpenMeteoClient,
    OpenMeteoConnectionError,
    OpenMeteoInvalidLocationError,
    OpenMeteoRateLimitError,
    OpenMeteoRequestError,
    const as c,
)

FORECAST = re.compile(r"^https://api\.open-meteo\.com/v1/forecast\?.*$")
AIR = re.compile(r"^https://air-quality-api\.open-meteo\.com/v1/air-quality\?.*$")


async def test_get_forecast(forecast_json) -> None:
    with aioresponses() as m:
        m.get(FORECAST, payload=forecast_json)
        async with OpenMeteoClient(55.64, 12.08, model="dmi_seamless") as client:
            fc = await client.get_forecast()
        assert fc.model == "dmi_seamless"
        ((key, calls),) = m.requests.items()
        url = str(key[1])
        assert "models=dmi_seamless" in url
        assert "timeformat=unixtime" in url
        assert "minutely_15=" in url
        assert calls[0].kwargs["headers"]["User-Agent"].startswith("aioopenmeteo/")


async def test_forecast_without_minutely(forecast_json) -> None:
    client = OpenMeteoClient(55.64, 12.08)
    params = client.forecast_params(minutely_15=False)
    assert "minutely_15" not in params
    assert params["models"] == "best_match"
    assert params["current"].split(",") == list(c.CURRENT_VARIABLES)


async def test_get_air_quality(air_quality_json) -> None:
    with aioresponses() as m:
        m.get(AIR, payload=air_quality_json)
        async with OpenMeteoClient(55.64, 12.08) as client:
            aq = await client.get_air_quality()
    assert aq.current is not None
    assert aq.current["pm2_5"] == 5.6


async def test_commercial_url(forecast_json) -> None:
    with aioresponses() as m:
        m.get(
            re.compile(r"^https://customer-api\.open-meteo\.com/.*apikey=secret.*"),
            payload=forecast_json,
        )
        async with OpenMeteoClient(55.64, 12.08, api_key="secret") as client:
            await client.get_forecast()


async def test_invalid_location() -> None:
    with aioresponses() as m:
        m.get(
            FORECAST,
            status=400,
            payload={"error": True, "reason": "No data is available for this location"},
        )
        async with OpenMeteoClient(55.64, 12.08, model="jma_msm") as client:
            with pytest.raises(OpenMeteoInvalidLocationError):
                await client.get_forecast()


async def test_bad_request() -> None:
    with aioresponses() as m:
        m.get(
            FORECAST,
            status=400,
            payload={"error": True, "reason": "Cannot initialize WeatherVariable"},
        )
        async with OpenMeteoClient(55.64, 12.08) as client:
            with pytest.raises(OpenMeteoRequestError) as err:
                await client.get_forecast()
    assert not isinstance(err.value, OpenMeteoInvalidLocationError)
    assert err.value.reason == "Cannot initialize WeatherVariable"


async def test_rate_limit() -> None:
    with aioresponses() as m:
        m.get(
            FORECAST,
            status=429,
            headers={"Retry-After": "60"},
            payload={"error": True, "reason": "Daily API request limit exceeded"},
        )
        async with OpenMeteoClient(55.64, 12.08) as client:
            with pytest.raises(OpenMeteoRateLimitError) as err:
                await client.get_forecast()
    assert err.value.retry_after == 60


async def test_connection_error() -> None:
    with aioresponses() as m:
        m.get(FORECAST, exception=TimeoutError())
        async with OpenMeteoClient(55.64, 12.08) as client:
            with pytest.raises(OpenMeteoConnectionError):
                await client.get_forecast()


def test_invalid_arguments() -> None:
    with pytest.raises(ValueError):
        OpenMeteoClient(95, 12)
    with pytest.raises(ValueError):
        OpenMeteoClient(55, 12, forecast_days=17)
