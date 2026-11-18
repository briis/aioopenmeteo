"""Constants for aioopenmeteo."""

from __future__ import annotations

from typing import Final

__version__: Final = "0.1.0"

FORECAST_URL: Final = "https://api.open-meteo.com/v1/forecast"
AIR_QUALITY_URL: Final = "https://air-quality-api.open-meteo.com/v1/air-quality"
# Commercial plans use the same paths on a "customer-" host plus an `apikey` parameter.
COMMERCIAL_FORECAST_URL: Final = "https://customer-api.open-meteo.com/v1/forecast"
COMMERCIAL_AIR_QUALITY_URL: Final = "https://customer-air-quality-api.open-meteo.com/v1/air-quality"

ATTRIBUTION: Final = "Weather data by Open-Meteo.com"
LICENSE_URL: Final = "https://creativecommons.org/licenses/by/4.0/"

DEFAULT_MODEL: Final = "best_match"
DEFAULT_FORECAST_DAYS: Final = 7
MAX_FORECAST_DAYS: Final = 16
DEFAULT_MINUTELY_15_STEPS: Final = 8  # two hours ahead
DEFAULT_TIMEOUT: Final = 30.0

# Units are always requested in the API defaults (metric):
#   temperature °C, wind km/h, precipitation mm, snowfall cm, snow depth m,
#   pressure hPa, visibility / heights m, radiation W/m², durations s.

CURRENT_VARIABLES: Final[tuple[str, ...]] = (
    "temperature_2m",
    "relative_humidity_2m",
    "dew_point_2m",
    "apparent_temperature",
    "wet_bulb_temperature_2m",
    "is_day",
    "weather_code",
    "precipitation",
    "precipitation_probability",
    "rain",
    "showers",
    "snowfall",
    "snow_depth",
    "cloud_cover",
    "cloud_cover_low",
    "cloud_cover_mid",
    "cloud_cover_high",
    "pressure_msl",
    "surface_pressure",
    "wind_speed_10m",
    "wind_direction_10m",
    "wind_gusts_10m",
    "wind_speed_80m",
    "wind_direction_80m",
    "visibility",
    "uv_index",
    "uv_index_clear_sky",
    "cape",
    "lifted_index",
    "convective_inhibition",
    "freezing_level_height",
    "boundary_layer_height",
    "vapour_pressure_deficit",
    "evapotranspiration",
    "et0_fao_evapotranspiration",
    "sunshine_duration",
    "shortwave_radiation",
    "direct_radiation",
    "diffuse_radiation",
    "direct_normal_irradiance",
    "terrestrial_radiation",
    "total_column_integrated_water_vapour",
    "soil_temperature_0cm",
    "soil_temperature_6cm",
    "soil_temperature_18cm",
    "soil_temperature_54cm",
    "soil_moisture_0_to_1cm",
    "soil_moisture_1_to_3cm",
    "soil_moisture_3_to_9cm",
    "soil_moisture_9_to_27cm",
    "soil_moisture_27_to_81cm",
)

# Hourly is the basis of an hourly forecast, so it is kept to what a forecast shows.
HOURLY_VARIABLES: Final[tuple[str, ...]] = (
    "temperature_2m",
    "apparent_temperature",
    "dew_point_2m",
    "relative_humidity_2m",
    "precipitation_probability",
    "precipitation",
    "weather_code",
    "pressure_msl",
    "cloud_cover",
    "wind_speed_10m",
    "wind_direction_10m",
    "wind_gusts_10m",
    "uv_index",
    "is_day",
    "visibility",
)

DAILY_VARIABLES: Final[tuple[str, ...]] = (
    "weather_code",
    "temperature_2m_max",
    "temperature_2m_min",
    "temperature_2m_mean",
    "apparent_temperature_max",
    "apparent_temperature_min",
    "dew_point_2m_mean",
    "relative_humidity_2m_mean",
    "pressure_msl_mean",
    "cloud_cover_mean",
    "uv_index_max",
    "uv_index_clear_sky_max",
    "sunrise",
    "sunset",
    "daylight_duration",
    "sunshine_duration",
    "moonrise",
    "moonset",
    "moon_phase",
    "precipitation_sum",
    "rain_sum",
    "showers_sum",
    "snowfall_sum",
    "precipitation_hours",
    "precipitation_probability_max",
    "wind_speed_10m_max",
    "wind_gusts_10m_max",
    "wind_direction_10m_dominant",
    "shortwave_radiation_sum",
    "et0_fao_evapotranspiration",
)

# Daily values that are points in time (unixtime in the response).
DAILY_TIMESTAMP_VARIABLES: Final = frozenset({"sunrise", "sunset", "moonrise", "moonset"})

# Native 15-minute data in Central Europe and North America, interpolated elsewhere.
MINUTELY_15_VARIABLES: Final[tuple[str, ...]] = (
    "precipitation",
    "rain",
    "snowfall",
    "weather_code",
    "sunshine_duration",
    "wind_gusts_10m",
    "lightning_potential",
)

AIR_QUALITY_CURRENT_VARIABLES: Final[tuple[str, ...]] = (
    "european_aqi",
    "european_aqi_pm2_5",
    "european_aqi_pm10",
    "european_aqi_nitrogen_dioxide",
    "european_aqi_ozone",
    "european_aqi_sulphur_dioxide",
    "us_aqi",
    "pm10",
    "pm2_5",
    "carbon_monoxide",
    "carbon_dioxide",
    "nitrogen_dioxide",
    "sulphur_dioxide",
    "ozone",
    "aerosol_optical_depth",
    "dust",
    "ammonia",
    "methane",
    "alder_pollen",
    "birch_pollen",
    "grass_pollen",
    "mugwort_pollen",
    "olive_pollen",
    "ragweed_pollen",
)

# Hourly air quality, used for "max in the next 24 hours" style values.
AIR_QUALITY_HOURLY_VARIABLES: Final[tuple[str, ...]] = (
    "european_aqi",
    "us_aqi",
    "pm2_5",
    "pm10",
    "alder_pollen",
    "birch_pollen",
    "grass_pollen",
    "mugwort_pollen",
    "olive_pollen",
    "ragweed_pollen",
)
DEFAULT_AIR_QUALITY_FORECAST_DAYS: Final = 2
