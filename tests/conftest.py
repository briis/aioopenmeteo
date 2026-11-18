"""Test fixtures: responses shaped like real Open-Meteo answers (timeformat=unixtime).

Built from live responses for Roskilde, Denmark (Europe/Copenhagen, UTC+1).
"""

from __future__ import annotations

from typing import Any

import pytest

from aioopenmeteo import const as c

# 2026-11-18 00:00 local (UTC+1) = 2026-11-17 23:00 UTC
DAY0 = 1794956400
NOW = 1795009500  # 2026-11-18 13:45 local

CURRENT_SAMPLE: dict[str, Any] = {
    "temperature_2m": 6.9,
    "relative_humidity_2m": 94,
    "dew_point_2m": 6.0,
    "apparent_temperature": 4.4,
    "wet_bulb_temperature_2m": 6.3,
    "is_day": 1,
    "weather_code": 55,
    "precipitation": 0.3,
    "precipitation_probability": 100,
    "rain": 0.3,
    "showers": 0,
    "snowfall": 0,
    "snow_depth": 0,
    "cloud_cover": 100,
    "pressure_msl": 974.3,
    "wind_speed_10m": 10.8,
    "wind_direction_10m": 135,
    "wind_gusts_10m": 40,
    "visibility": 3200,
    "uv_index": 0.05,
    "cape": 20,
    "lifted_index": None,
    "evapotranspiration": None,
    "soil_temperature_0cm": 6.2,
}


def forecast_payload(days_with_data: int = 7, forecast_days: int = 7) -> dict[str, Any]:
    """A forecast response; days after `days_with_data` are null like a short model."""
    hours = forecast_days * 24
    with_data = days_with_data * 24
    hourly: dict[str, list] = {"time": [DAY0 + 3600 * i for i in range(hours)]}
    for name in c.HOURLY_VARIABLES:
        if name == "is_day":
            hourly[name] = [1 if 8 <= i % 24 < 16 else 0 for i in range(hours)]
        elif name == "weather_code":
            hourly[name] = [3 if i < with_data else None for i in range(hours)]
        else:
            hourly[name] = [float(i % 24) if i < with_data else None for i in range(hours)]
    daily: dict[str, list] = {"time": [DAY0 + 86400 * d for d in range(forecast_days)]}
    for name in c.DAILY_VARIABLES:
        if name in ("sunrise", "sunset", "moonrise"):
            offset = {"sunrise": 28341, "sunset": 57642, "moonrise": 49436}[name]
            daily[name] = [DAY0 + 86400 * d + offset for d in range(forecast_days)]
        elif name == "moonset":
            daily[name] = [None] + [DAY0 + 86400 * d + 70000 for d in range(1, forecast_days)]
        elif name in ("daylight_duration", "moon_phase"):
            daily[name] = [29296.42 if name == "daylight_duration" else 0.28] * forecast_days
        elif name == "weather_code":
            daily[name] = [61 if d < days_with_data else None for d in range(forecast_days)]
        else:
            daily[name] = [float(d) if d < days_with_data else None for d in range(forecast_days)]
    quarters = 8
    minutely: dict[str, list] = {"time": [NOW + 900 * i for i in range(quarters)]}
    for name in c.MINUTELY_15_VARIABLES:
        minutely[name] = [None] * quarters if name == "lightning_potential" else [0.3] * quarters
    return {
        "latitude": 55.640255,
        "longitude": 12.082382,
        "generationtime_ms": 3.2,
        "utc_offset_seconds": 3600,
        "timezone": "Europe/Copenhagen",
        "timezone_abbreviation": "GMT+1",
        "elevation": 45.0,
        "current_units": {"time": "unixtime", "interval": "seconds", "temperature_2m": "°C"},
        "current": {"time": NOW, "interval": 900, **CURRENT_SAMPLE},
        "minutely_15_units": {"time": "unixtime", "precipitation": "mm"},
        "minutely_15": minutely,
        "hourly_units": {"time": "unixtime", "wind_speed_10m": "km/h"},
        "hourly": hourly,
        "daily_units": {"time": "unixtime", "snowfall_sum": "cm"},
        "daily": daily,
    }


def air_quality_payload() -> dict[str, Any]:
    current = {
        "time": 1795006800,
        "interval": 3600,
        "european_aqi": 22,
        "us_aqi": 23,
        "pm10": 6.4,
        "pm2_5": 5.6,
        "birch_pollen": 0,
        "olive_pollen": 0,
        "nitrogen_dioxide": 11.8,
    }
    hours = 48
    hourly = {
        "time": [DAY0 + 3600 * i for i in range(hours)],
        "european_aqi": [16 + (i % 24) for i in range(hours)],
        "birch_pollen": [None] * hours,
    }
    return {
        "latitude": 55.6,
        "longitude": 12.1,
        "generationtime_ms": 1.0,
        "utc_offset_seconds": 3600,
        "timezone": "Europe/Copenhagen",
        "timezone_abbreviation": "GMT+1",
        "elevation": 45.0,
        "current_units": {"european_aqi": "EAQI", "pm2_5": "μg/m³"},
        "current": current,
        "hourly_units": {"european_aqi": "EAQI"},
        "hourly": hourly,
    }


@pytest.fixture
def forecast_json() -> dict[str, Any]:
    return forecast_payload()


@pytest.fixture
def air_quality_json() -> dict[str, Any]:
    return air_quality_payload()
