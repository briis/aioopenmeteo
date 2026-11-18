"""Data classes returned by the client.

Values are kept by their Open-Meteo variable name (e.g. "temperature_2m"), so every
variable the API returns is available without a hand-written field for each one.
A variable the selected model does not provide is None.
"""

from __future__ import annotations

from collections.abc import Iterator, Mapping
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta

from .conditions import condition_from_wmo, moon_phase_name, wmo_description, wmo_key

Value = float | int | datetime | None

_QUARTER = timedelta(minutes=15)
_HOUR = timedelta(hours=1)
_DAY = timedelta(days=1)


@dataclass(slots=True)
class DataPoint(Mapping[str, Value]):
    """Values at one point in time (current, one hour, one quarter)."""

    time: datetime
    values: dict[str, Value] = field(default_factory=dict)

    def __getitem__(self, key: str) -> Value:
        return self.values[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self.values)

    def __len__(self) -> int:
        return len(self.values)

    @property
    def is_day(self) -> bool | None:
        value = self.values.get("is_day")
        return None if value is None else bool(value)

    @property
    def condition(self) -> str | None:
        """Home Assistant weather condition from the weather code."""
        return condition_from_wmo(self.values.get("weather_code"), self.is_day)

    @property
    def weather_key(self) -> str | None:
        return wmo_key(self.values.get("weather_code"))

    @property
    def weather_description(self) -> str | None:
        return wmo_description(self.values.get("weather_code"))


@dataclass(slots=True)
class DailyForecast(Mapping[str, Value]):
    """One day. `date` is the local date; sunrise etc. are aware datetimes (UTC)."""

    date: date
    start: datetime  # local midnight as an aware datetime
    values: dict[str, Value] = field(default_factory=dict)

    def __getitem__(self, key: str) -> Value:
        return self.values[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self.values)

    def __len__(self) -> int:
        return len(self.values)

    @property
    def condition(self) -> str | None:
        return condition_from_wmo(self.values.get("weather_code"), True)

    @property
    def weather_key(self) -> str | None:
        return wmo_key(self.values.get("weather_code"))

    @property
    def moon_phase(self) -> str | None:
        value = self.values.get("moon_phase")
        return moon_phase_name(value) if isinstance(value, int | float) else None


@dataclass(slots=True)
class Forecast:
    """A complete forecast for one location and model."""

    latitude: float
    longitude: float
    elevation: float | None
    timezone: str
    utc_offset_seconds: int
    model: str
    fetched_at: datetime
    current: DataPoint | None
    hourly: list[DataPoint] = field(default_factory=list)
    daily: list[DailyForecast] = field(default_factory=list)
    minutely_15: list[DataPoint] = field(default_factory=list)
    units: dict[str, str] = field(default_factory=dict)

    def hourly_from(self, start: datetime) -> list[DataPoint]:
        """Hours from the one containing `start` onwards."""
        hour = start.replace(minute=0, second=0, microsecond=0)
        return [h for h in self.hourly if h.time >= hour]

    def minutely_15_from(self, start: datetime) -> list[DataPoint]:
        """Quarters from the one containing `start` onwards."""
        return [m for m in self.minutely_15 if m.time + _QUARTER > start]

    def today(self, now: datetime) -> DailyForecast | None:
        """The day containing `now`, in the location's time zone."""
        for day in self.daily:
            if day.start <= now < day.start + _DAY:
                return day
        return None

    def available(self, section: str = "current") -> set[str]:
        """Variables with a value in a section ('current', 'hourly', 'daily', 'minutely_15').

        Useful to decide which sensors to create for a model.
        """
        if section == "current":
            points: list = [self.current] if self.current else []
        else:
            points = getattr(self, section)
        return {k for p in points for k, v in p.values.items() if v is not None}


@dataclass(slots=True)
class AirQuality:
    """Current air quality and pollen, plus a short hourly forecast."""

    latitude: float
    longitude: float
    fetched_at: datetime
    current: DataPoint | None
    hourly: list[DataPoint] = field(default_factory=list)
    units: dict[str, str] = field(default_factory=dict)

    def max_next(self, key: str, start: datetime, hours: int = 24) -> float | None:
        """Highest value of `key` from the current hour and `hours` ahead."""
        end = start + hours * _HOUR
        values = [
            v
            for h in self.hourly
            if start - _HOUR < h.time <= end and isinstance(v := h.values.get(key), int | float)
        ]
        return max(values) if values else None

    def available(self) -> set[str]:
        if self.current is None:
            return set()
        return {k for k, v in self.current.values.items() if v is not None}
