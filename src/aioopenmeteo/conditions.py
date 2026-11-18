"""WMO weather codes, as used by Open-Meteo, and what they mean.

Condition strings match Home Assistant's weather conditions, so the library can be
used without importing Home Assistant.
"""

from __future__ import annotations

# code -> (key, English description)
WMO_CODES: dict[int, tuple[str, str]] = {
    0: ("clear_sky", "Clear sky"),
    1: ("mainly_clear", "Mainly clear"),
    2: ("partly_cloudy", "Partly cloudy"),
    3: ("overcast", "Overcast"),
    45: ("fog", "Fog"),
    48: ("depositing_rime_fog", "Depositing rime fog"),
    51: ("drizzle_light", "Light drizzle"),
    53: ("drizzle_moderate", "Moderate drizzle"),
    55: ("drizzle_dense", "Dense drizzle"),
    56: ("freezing_drizzle_light", "Light freezing drizzle"),
    57: ("freezing_drizzle_dense", "Dense freezing drizzle"),
    61: ("rain_slight", "Slight rain"),
    63: ("rain_moderate", "Moderate rain"),
    65: ("rain_heavy", "Heavy rain"),
    66: ("freezing_rain_light", "Light freezing rain"),
    67: ("freezing_rain_heavy", "Heavy freezing rain"),
    71: ("snow_slight", "Slight snowfall"),
    73: ("snow_moderate", "Moderate snowfall"),
    75: ("snow_heavy", "Heavy snowfall"),
    77: ("snow_grains", "Snow grains"),
    80: ("rain_showers_slight", "Slight rain showers"),
    81: ("rain_showers_moderate", "Moderate rain showers"),
    82: ("rain_showers_violent", "Violent rain showers"),
    85: ("snow_showers_slight", "Slight snow showers"),
    86: ("snow_showers_heavy", "Heavy snow showers"),
    95: ("thunderstorm", "Thunderstorm"),
    96: ("thunderstorm_slight_hail", "Thunderstorm with slight hail"),
    99: ("thunderstorm_heavy_hail", "Thunderstorm with heavy hail"),
}

WMO_KEYS: tuple[str, ...] = tuple(key for key, _ in WMO_CODES.values())

_CONDITIONS: dict[int, str] = {
    0: "sunny",
    1: "sunny",
    2: "partlycloudy",
    3: "cloudy",
    45: "fog",
    48: "fog",
    51: "rainy",
    53: "rainy",
    55: "rainy",
    56: "snowy-rainy",
    57: "snowy-rainy",
    61: "rainy",
    63: "rainy",
    65: "pouring",
    66: "snowy-rainy",
    67: "snowy-rainy",
    71: "snowy",
    73: "snowy",
    75: "snowy",
    77: "snowy",
    80: "rainy",
    81: "rainy",
    82: "pouring",
    85: "snowy",
    86: "snowy",
    95: "lightning-rainy",
    96: "hail",
    99: "hail",
}


def wmo_key(code: int | float | None) -> str | None:
    """Short key for a WMO code ('rain_moderate'), or None if unknown."""
    if code is None:
        return None
    item = WMO_CODES.get(int(code))
    return item[0] if item else None


def wmo_description(code: int | float | None) -> str | None:
    """English description of a WMO code, or None if unknown."""
    if code is None:
        return None
    item = WMO_CODES.get(int(code))
    return item[1] if item else None


def condition_from_wmo(code: int | float | None, is_day: bool | int | None = True) -> str | None:
    """Home Assistant weather condition for a WMO code.

    Clear sky at night is 'clear-night'. `is_day=None` is treated as day.
    """
    if code is None:
        return None
    condition = _CONDITIONS.get(int(code))
    if condition == "sunny" and is_day is not None and not is_day:
        return "clear-night"
    return condition


def moon_phase_name(fraction: float | None) -> str | None:
    """Name of the moon phase for Open-Meteo's fraction (0 new, 0.25 first quarter,
    0.5 full, 0.75 last quarter). Names match Home Assistant's moon sensor."""
    if fraction is None:
        return None
    f = fraction % 1.0
    # The four principal phases get a window of one day either side (~0.034).
    window = 1 / 29.53
    for center, name in (
        (0.0, "new_moon"),
        (0.25, "first_quarter"),
        (0.5, "full_moon"),
        (0.75, "last_quarter"),
        (1.0, "new_moon"),
    ):
        if abs(f - center) <= window:
            return name
    if f < 0.25:
        return "waxing_crescent"
    if f < 0.5:
        return "waxing_gibbous"
    if f < 0.75:
        return "waning_gibbous"
    return "waning_crescent"
