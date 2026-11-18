"""Turn Open-Meteo JSON (requested with timeformat=unixtime) into data classes."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta, timezone
from typing import Any

from .const import DAILY_TIMESTAMP_VARIABLES
from .exceptions import OpenMeteoParseError
from .models import AirQuality, DailyForecast, DataPoint, Forecast, Value


def _utc(ts: Any) -> datetime:
    if not isinstance(ts, int | float):
        raise OpenMeteoParseError(f"Expected a unix time, got {ts!r}")
    return datetime.fromtimestamp(ts, UTC)


def _current(section: Any) -> DataPoint | None:
    if not isinstance(section, dict) or "time" not in section:
        return None
    values = {k: v for k, v in section.items() if k not in ("time", "interval")}
    return DataPoint(_utc(section["time"]), values)


def _series(section: Any) -> list[tuple[Any, dict[str, Any]]]:
    """Column arrays -> rows of (time, values)."""
    if not isinstance(section, dict) or not isinstance(section.get("time"), list):
        return []
    times = section["time"]
    columns = {k: v for k, v in section.items() if k != "time" and isinstance(v, list)}
    for name, column in columns.items():
        if len(column) != len(times):
            raise OpenMeteoParseError(
                f"Column {name!r} has {len(column)} values, expected {len(times)}"
            )
    return [(t, {k: col[i] for k, col in columns.items()}) for i, t in enumerate(times)]


def _trim(rows: list[Any]) -> list[Any]:
    """Drop rows at the end where every value is None.

    The API pads every model to the requested number of days; a model with a short
    horizon (e.g. DMI Harmonie, ~2.5 days) has only nulls after that. `is_day` is
    astronomical and present beyond the horizon, so it does not count.
    """
    while rows and all(v is None for k, v in rows[-1].values.items() if k != "is_day"):
        rows.pop()
    return rows


def _points(section: Any) -> list[DataPoint]:
    return _trim([DataPoint(_utc(t), values) for t, values in _series(section)])


def _days(section: Any, tz: timezone) -> list[DailyForecast]:
    days: list[DailyForecast] = []
    for t, raw in _series(section):
        start = _utc(t).astimezone(tz)
        values: dict[str, Value] = {}
        for key, value in raw.items():
            if key in DAILY_TIMESTAMP_VARIABLES and value is not None:
                values[key] = _utc(value)
            else:
                values[key] = value
        days.append(DailyForecast(start.date(), start, values))
    # A day with only astronomy (sunrise, moon) but no weather is past the horizon.
    while days and all(v is None for k, v in days[-1].values.items() if k not in _ASTRONOMY):
        days.pop()
    return days


_ASTRONOMY = DAILY_TIMESTAMP_VARIABLES | {"daylight_duration", "moon_phase"}


def _units(data: dict[str, Any]) -> dict[str, str]:
    units: dict[str, str] = {}
    for section in ("current_units", "hourly_units", "daily_units", "minutely_15_units"):
        for key, unit in (data.get(section) or {}).items():
            if key not in ("time", "interval") and isinstance(unit, str):
                units.setdefault(key, unit)
    return units


def parse_forecast(data: Any, model: str, fetched_at: datetime | None = None) -> Forecast:
    """Parse a /v1/forecast response for a single location and model."""
    if not isinstance(data, dict):
        raise OpenMeteoParseError(f"Expected a JSON object, got {type(data).__name__}")
    try:
        offset = int(data.get("utc_offset_seconds") or 0)
        tz = timezone(timedelta(seconds=offset))
        return Forecast(
            latitude=float(data["latitude"]),
            longitude=float(data["longitude"]),
            elevation=data.get("elevation"),
            timezone=str(data.get("timezone") or "GMT"),
            utc_offset_seconds=offset,
            model=model,
            fetched_at=fetched_at or datetime.now(UTC),
            current=_current(data.get("current")),
            hourly=_points(data.get("hourly")),
            daily=_days(data.get("daily"), tz),
            minutely_15=_points(data.get("minutely_15")),
            units=_units(data),
        )
    except (KeyError, TypeError, ValueError) as err:
        raise OpenMeteoParseError(f"Unexpected forecast response: {err!r}") from err


def parse_air_quality(data: Any, fetched_at: datetime | None = None) -> AirQuality:
    """Parse an /v1/air-quality response for a single location."""
    if not isinstance(data, dict):
        raise OpenMeteoParseError(f"Expected a JSON object, got {type(data).__name__}")
    try:
        return AirQuality(
            latitude=float(data["latitude"]),
            longitude=float(data["longitude"]),
            fetched_at=fetched_at or datetime.now(UTC),
            current=_current(data.get("current")),
            hourly=_points(data.get("hourly")),
            units=_units(data),
        )
    except (KeyError, TypeError, ValueError) as err:
        raise OpenMeteoParseError(f"Unexpected air quality response: {err!r}") from err
