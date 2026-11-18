"""Client tests against a local aiohttp test server (no mocking library needed)."""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

from aiohttp import web
from aiohttp.test_utils import TestServer
import pytest

from aioopenmeteo import (
    OpenMeteoClient,
    OpenMeteoConnectionError,
    OpenMeteoInvalidLocationError,
    OpenMeteoRateLimitError,
    OpenMeteoRequestError,
    const as c,
)


class FakeOpenMeteo:
    """Answers like Open-Meteo; records the requests it gets."""

    def __init__(self) -> None:
        self.requests: list[web.Request] = []
        self.status = 200
        self.payload: Any = {}
        self.headers: dict[str, str] = {}

    async def handle(self, request: web.Request) -> web.Response:
        self.requests.append(request)
        return web.json_response(self.payload, status=self.status, headers=self.headers)


@pytest.fixture
async def fake(monkeypatch) -> AsyncIterator[FakeOpenMeteo]:
    fake = FakeOpenMeteo()
    app = web.Application()
    app.router.add_get("/{path:.*}", fake.handle)
    server = TestServer(app)
    await server.start_server()
    base = str(server.make_url("")).rstrip("/")
    monkeypatch.setattr(c, "FORECAST_URL", f"{base}/v1/forecast")
    monkeypatch.setattr(c, "AIR_QUALITY_URL", f"{base}/v1/air-quality")
    monkeypatch.setattr(c, "COMMERCIAL_FORECAST_URL", f"{base}/customer/v1/forecast")
    yield fake
    await server.close()


async def test_get_forecast(fake, forecast_json) -> None:
    fake.payload = forecast_json
    async with OpenMeteoClient(55.64, 12.08, model="dmi_seamless") as client:
        fc = await client.get_forecast()
    assert fc.model == "dmi_seamless"
    request = fake.requests[0]
    assert request.path == "/v1/forecast"
    assert request.query["models"] == "dmi_seamless"
    assert request.query["timeformat"] == "unixtime"
    assert "minutely_15" in request.query
    assert request.headers["User-Agent"].startswith("aioopenmeteo/")


async def test_forecast_without_minutely() -> None:
    client = OpenMeteoClient(55.64, 12.08)
    params = client.forecast_params(minutely_15=False)
    assert "minutely_15" not in params
    assert params["models"] == "best_match"
    assert params["current"].split(",") == list(c.CURRENT_VARIABLES)


async def test_get_air_quality(fake, air_quality_json) -> None:
    fake.payload = air_quality_json
    async with OpenMeteoClient(55.64, 12.08) as client:
        aq = await client.get_air_quality()
    assert fake.requests[0].path == "/v1/air-quality"
    assert fake.requests[0].query["domains"] == "auto"
    assert aq.current is not None
    assert aq.current["pm2_5"] == 5.6


async def test_commercial_url(fake, forecast_json) -> None:
    fake.payload = forecast_json
    async with OpenMeteoClient(55.64, 12.08, api_key="secret") as client:
        await client.get_forecast()
    assert fake.requests[0].path == "/customer/v1/forecast"
    assert fake.requests[0].query["apikey"] == "secret"


async def test_invalid_location(fake) -> None:
    fake.status = 400
    fake.payload = {"error": True, "reason": "No data is available for this location"}
    async with OpenMeteoClient(55.64, 12.08, model="jma_msm") as client:
        with pytest.raises(OpenMeteoInvalidLocationError):
            await client.get_forecast()


async def test_bad_request(fake) -> None:
    fake.status = 400
    fake.payload = {"error": True, "reason": "Cannot initialize WeatherVariable"}
    async with OpenMeteoClient(55.64, 12.08) as client:
        with pytest.raises(OpenMeteoRequestError) as err:
            await client.get_forecast()
    assert not isinstance(err.value, OpenMeteoInvalidLocationError)
    assert err.value.reason == "Cannot initialize WeatherVariable"


async def test_rate_limit(fake) -> None:
    fake.status = 429
    fake.headers = {"Retry-After": "60"}
    fake.payload = {"error": True, "reason": "Daily API request limit exceeded"}
    async with OpenMeteoClient(55.64, 12.08) as client:
        with pytest.raises(OpenMeteoRateLimitError) as err:
            await client.get_forecast()
    assert err.value.retry_after == 60


async def test_connection_error(monkeypatch) -> None:
    # Nothing listens on port 9 (discard) on the test host.
    monkeypatch.setattr(c, "FORECAST_URL", "http://127.0.0.1:9/v1/forecast")
    async with OpenMeteoClient(55.64, 12.08, timeout=5) as client:
        with pytest.raises(OpenMeteoConnectionError):
            await client.get_forecast()


def test_invalid_arguments() -> None:
    with pytest.raises(ValueError):
        OpenMeteoClient(95, 12)
    with pytest.raises(ValueError):
        OpenMeteoClient(55, 12, forecast_days=17)
