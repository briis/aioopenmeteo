"""Parser and data model tests."""

from __future__ import annotations

from datetime import UTC, date, datetime, timedelta

import pytest

from aioopenmeteo import (
    OpenMeteoParseError,
    condition_from_wmo,
    get_model,
    moon_phase_name,
    parse_air_quality,
    parse_forecast,
    wmo_key,
)

from .conftest import DAY0, NOW, forecast_payload


def test_parse_forecast(forecast_json) -> None:
    fc = parse_forecast(forecast_json, "best_match")
    assert fc.model == "best_match"
    assert fc.timezone == "Europe/Copenhagen"
    assert fc.current is not None
    assert fc.current.time == datetime.fromtimestamp(NOW, UTC)
    assert fc.current["temperature_2m"] == 6.9
    assert "interval" not in fc.current
    assert fc.current.condition == "rainy"
    assert fc.current.weather_key == "drizzle_dense"
    assert len(fc.hourly) == 7 * 24
    assert len(fc.daily) == 7
    assert len(fc.minutely_15) == 8
    assert fc.units["temperature_2m"] == "°C"


def test_daily_dates_and_timestamps(forecast_json) -> None:
    fc = parse_forecast(forecast_json, "best_match")
    day = fc.daily[0]
    assert day.date == date(2026, 11, 18)
    assert day.start.utcoffset() == timedelta(hours=1)
    assert isinstance(day["sunrise"], datetime)
    assert day["sunrise"] == datetime.fromtimestamp(DAY0 + 28341, UTC)
    assert day["moonset"] is None
    assert day.moon_phase == "first_quarter"


def test_short_model_is_trimmed() -> None:
    """A model with ~2 days of data padded with nulls to 7 days gets trimmed."""
    fc = parse_forecast(forecast_payload(days_with_data=2), "dmi_harmonie_arome_europe")
    assert len(fc.daily) == 2
    assert len(fc.hourly) == 48
    assert all(h["temperature_2m"] is not None for h in fc.hourly)


def test_available(forecast_json) -> None:
    fc = parse_forecast(forecast_json, "best_match")
    available = fc.available()
    assert "temperature_2m" in available
    assert "lifted_index" not in available
    assert "lightning_potential" not in fc.available("minutely_15")
    assert "precipitation" in fc.available("minutely_15")


def test_today_and_hourly_from(forecast_json) -> None:
    fc = parse_forecast(forecast_json, "best_match")
    now = datetime.fromtimestamp(NOW, UTC)
    today = fc.today(now)
    assert today is not None
    assert today.date == date(2026, 11, 18)
    hours = fc.hourly_from(now)
    assert hours[0].time == now.replace(minute=0)
    quarters = fc.minutely_15_from(now)
    assert quarters[0].time == now


def test_parse_errors() -> None:
    with pytest.raises(OpenMeteoParseError):
        parse_forecast([], "best_match")
    with pytest.raises(OpenMeteoParseError):
        parse_forecast({"longitude": 1}, "best_match")
    bad = forecast_payload()
    bad["hourly"]["temperature_2m"] = bad["hourly"]["temperature_2m"][:3]
    with pytest.raises(OpenMeteoParseError):
        parse_forecast(bad, "best_match")


def test_parse_air_quality(air_quality_json) -> None:
    aq = parse_air_quality(air_quality_json)
    assert aq.current is not None
    assert aq.current["european_aqi"] == 22
    assert "birch_pollen" in aq.available()
    # hourly birch pollen is all null -> those values are skipped
    start = datetime.fromtimestamp(DAY0, UTC)
    assert aq.max_next("birch_pollen", start) is None
    assert aq.max_next("european_aqi", start, hours=5) == 21


@pytest.mark.parametrize(
    ("code", "is_day", "expected"),
    [
        (0, 1, "sunny"),
        (0, 0, "clear-night"),
        (1, False, "clear-night"),
        (2, 0, "partlycloudy"),
        (45, 1, "fog"),
        (65, 1, "pouring"),
        (66, 1, "snowy-rainy"),
        (75, 1, "snowy"),
        (95, 1, "lightning-rainy"),
        (99, 1, "hail"),
        (None, 1, None),
        (42, 1, None),
    ],
)
def test_condition_from_wmo(code, is_day, expected) -> None:
    assert condition_from_wmo(code, is_day) == expected


def test_wmo_key_and_moon() -> None:
    assert wmo_key(63.0) == "rain_moderate"
    assert wmo_key(None) is None
    assert moon_phase_name(0.0) == "new_moon"
    assert moon_phase_name(0.99) == "new_moon"
    assert moon_phase_name(0.1) == "waxing_crescent"
    assert moon_phase_name(0.25) == "first_quarter"
    assert moon_phase_name(0.5) == "full_moon"
    assert moon_phase_name(0.6) == "waning_gibbous"
    assert moon_phase_name(0.75) == "last_quarter"
    assert moon_phase_name(0.85) == "waning_crescent"


def test_models() -> None:
    assert get_model("best_match").name == "Best match"
    assert get_model("dmi_seamless").provider == "DMI"
    assert get_model("some_new_model").name == "some_new_model"


def test_real_response_short_model() -> None:
    """Real DMI Harmonie response for Roskilde (2026-11-18): ~70 h of data in 4 days."""
    import json
    from pathlib import Path

    data = json.loads(
        (Path(__file__).parent / "fixtures" / "dmi_harmonie_roskilde.json").read_text()
    )
    fc = parse_forecast(data, "dmi_harmonie_arome_europe")
    assert len(fc.hourly) == 70  # trailing null hours dropped (is_day ignored)
    assert len(fc.daily) == 2  # partial and empty days dropped
    assert fc.daily[0].date == date(2026, 11, 18)
    assert fc.daily[1]["moonset"] is not None
    assert fc.current is not None
    assert fc.current.condition == "rainy"
    assert "uv_index" not in fc.available()
    assert "uv_index" not in fc.available("hourly")
    assert "lightning_potential" not in fc.available("minutely_15")
    assert fc.hourly[-1].condition == "clear-night"
