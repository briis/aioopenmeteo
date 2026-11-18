# aioopenmeteo

Async Python client for the free [Open-Meteo](https://open-meteo.com) weather forecast and air quality APIs, written for the [Open-Meteo Home Assistant integration](https://github.com/briis/ha-openmeteo).

- Pick any of Open-Meteo's ~50 weather models, or **Best match** (the default).
- One request gets current conditions (50+ variables), hourly and daily forecasts and 15-minute data.
- Air quality and pollen (CAMS Europe / global) from the separate air quality API.
- Values are kept by their Open-Meteo variable name, so everything the API returns is available.
- Variables a model doesn't provide are `None`, and days past a model's horizon are dropped.
- WMO weather codes mapped to Home Assistant conditions, plus moon phase names.

## Install

```bash
pip install aioopenmeteo
```

## Usage

```python
import asyncio
from aioopenmeteo import OpenMeteoClient


async def main() -> None:
    async with OpenMeteoClient(55.64, 12.08, model="dmi_seamless", forecast_days=7) as client:
        forecast = await client.get_forecast()
        now = forecast.current
        print(now["temperature_2m"], now["wind_speed_10m"], now.condition)

        for day in forecast.daily:
            print(day.date, day["temperature_2m_min"], day["temperature_2m_max"], day.condition)

        air = await client.get_air_quality()
        print(air.current["european_aqi"], air.current["birch_pollen"])


asyncio.run(main())
```

In Home Assistant, pass the shared session: `OpenMeteoClient(lat, lon, session=async_get_clientsession(hass))`.

### Models

`aioopenmeteo.MODELS` lists the selectable models (`id`, `name`, `provider`, `regional`). Regional models (e.g. `dmi_harmonie_arome_europe`, `jma_msm`) only cover part of the world. Elsewhere the API answers with an error, raised as `OpenMeteoInvalidLocationError`.

`forecast.available("current")` returns the variables the chosen model actually has values for. This is useful for deciding which sensors to create.

### Units

Data is always requested in Open-Meteo's default metric units:
- temperature in °C
- wind in km/h
- precipitation in mm (snowfall in cm, snow depth in m)
- pressure in hPa
- visibility in m
- radiation in W/m²
- durations in seconds

### Errors

| Exception | When |
|---|---|
| `OpenMeteoConnectionError` | Network problem or timeout |
| `OpenMeteoInvalidLocationError` | The model has no data for the location |
| `OpenMeteoRateLimitError` | Free limit reached (HTTP 429) |
| `OpenMeteoRequestError` | Any other HTTP error, `reason` from the API |
| `OpenMeteoParseError` | Unexpected response |

All of them derive from `OpenMeteoError`.

## Terms and attribution

The free API is for **non-commercial use**, within 10,000 calls per day, 5,000 per hour and 600 per minute. Large requests count as more than one call. Data is licensed [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/), so show `aioopenmeteo.ATTRIBUTION` ("Weather data by Open-Meteo.com") with it. For commercial use, get an API key from Open-Meteo and pass `api_key=...`, which uses the `customer-` API hosts.

## License

MIT
