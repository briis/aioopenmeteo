"""aioopenmeteo - async client for the Open-Meteo forecast and air quality APIs.

    from aioopenmeteo import OpenMeteoClient

    async with OpenMeteoClient(55.64, 12.08, model="dmi_seamless") as client:
        forecast = await client.get_forecast()
        print(forecast.current["temperature_2m"], forecast.current.condition)

Data: Open-Meteo.com, CC BY 4.0 - show `ATTRIBUTION` with the data.
"""

from .client import OpenMeteoClient
from .conditions import (
    WMO_CODES,
    WMO_KEYS,
    condition_from_wmo,
    moon_phase_name,
    wmo_description,
    wmo_key,
)
from .const import (
    AIR_QUALITY_CURRENT_VARIABLES,
    ATTRIBUTION,
    CURRENT_VARIABLES,
    DAILY_VARIABLES,
    DEFAULT_FORECAST_DAYS,
    DEFAULT_MODEL,
    HOURLY_VARIABLES,
    LICENSE_URL,
    MAX_FORECAST_DAYS,
    MINUTELY_15_VARIABLES,
    __version__,
)
from .exceptions import (
    OpenMeteoConnectionError,
    OpenMeteoError,
    OpenMeteoInvalidLocationError,
    OpenMeteoParseError,
    OpenMeteoRateLimitError,
    OpenMeteoRequestError,
)
from .models import AirQuality, DailyForecast, DataPoint, Forecast
from .parser import parse_air_quality, parse_forecast
from .weather_models import MODELS, MODELS_BY_ID, WeatherModel, get_model

__all__ = [
    "AIR_QUALITY_CURRENT_VARIABLES",
    "ATTRIBUTION",
    "CURRENT_VARIABLES",
    "DAILY_VARIABLES",
    "DEFAULT_FORECAST_DAYS",
    "DEFAULT_MODEL",
    "HOURLY_VARIABLES",
    "LICENSE_URL",
    "MAX_FORECAST_DAYS",
    "MINUTELY_15_VARIABLES",
    "MODELS",
    "MODELS_BY_ID",
    "WMO_CODES",
    "WMO_KEYS",
    "AirQuality",
    "DailyForecast",
    "DataPoint",
    "Forecast",
    "OpenMeteoClient",
    "OpenMeteoConnectionError",
    "OpenMeteoError",
    "OpenMeteoInvalidLocationError",
    "OpenMeteoParseError",
    "OpenMeteoRateLimitError",
    "OpenMeteoRequestError",
    "WeatherModel",
    "__version__",
    "condition_from_wmo",
    "get_model",
    "moon_phase_name",
    "parse_air_quality",
    "parse_forecast",
    "wmo_description",
    "wmo_key",
]
