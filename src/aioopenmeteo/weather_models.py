"""Weather models offered by the Open-Meteo forecast API.

Identifiers come from the `models` parameter of https://open-meteo.com/en/docs.
Models Open-Meteo has announced as discontinued are left out.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class WeatherModel:
    """One selectable model."""

    id: str
    name: str
    provider: str
    regional: bool = False  # only covers part of the world (400 elsewhere)


MODELS: tuple[WeatherModel, ...] = (
    WeatherModel("best_match", "Best match", "Open-Meteo"),
    # ECMWF
    WeatherModel("ecmwf_ifs", "ECMWF IFS HRES 9 km", "ECMWF"),
    WeatherModel("ecmwf_ifs025", "ECMWF IFS 0.25°", "ECMWF"),
    WeatherModel("ecmwf_aifs025_single", "ECMWF AIFS 0.25° Single", "ECMWF"),
    # CMA
    WeatherModel("cma_grapes_global", "CMA GRAPES Global", "CMA"),
    # NOAA NCEP
    WeatherModel("ncep_gfs_seamless", "NCEP GFS Seamless", "NOAA NCEP"),
    WeatherModel("ncep_gfs_global", "NCEP GFS Global 0.11°/0.25°", "NOAA NCEP"),
    WeatherModel("ncep_rrfs_north_america", "NCEP RRFS North America", "NOAA NCEP", True),
    WeatherModel("ncep_rrfs_conus", "NCEP RRFS U.S. CONUS", "NOAA NCEP", True),
    WeatherModel("ncep_nbm_conus", "NCEP NBM U.S. CONUS", "NOAA NCEP", True),
    WeatherModel("ncep_aigfs025", "NCEP AIGFS 0.25°", "NOAA NCEP"),
    WeatherModel("ncep_hgefs025_ensemble_mean", "NCEP HGEFS 0.25° Ensemble Mean", "NOAA NCEP"),
    # JMA
    WeatherModel("jma_seamless", "JMA Seamless", "JMA"),
    WeatherModel("jma_msm", "JMA MSM", "JMA", True),
    WeatherModel("jma_gsm", "JMA GSM", "JMA"),
    # DWD
    WeatherModel("dwd_icon_seamless", "DWD ICON Seamless", "DWD"),
    WeatherModel("dwd_icon_global_native", "DWD ICON Global", "DWD"),
    WeatherModel("dwd_aicon_global_native", "DWD AICON Global", "DWD"),
    WeatherModel("dwd_icon_eu_native", "DWD ICON EU", "DWD", True),
    WeatherModel("dwd_icon_d2_native", "DWD ICON D2", "DWD", True),
    WeatherModel("dwd_icon_d2_ruc_native", "DWD ICON D2 RUC", "DWD", True),
    # Environment Canada
    WeatherModel("cmc_gem_seamless", "GEM Seamless", "Environment Canada"),
    WeatherModel("cmc_gem_gdps", "GEM Global", "Environment Canada"),
    WeatherModel("cmc_gem_rdps", "GEM Regional", "Environment Canada", True),
    WeatherModel("cmc_gem_hrdps", "GEM HRDPS Continental", "Environment Canada", True),
    WeatherModel("cmc_gem_hrdps_west", "GEM HRDPS West", "Environment Canada", True),
    # Météo-France
    WeatherModel("meteofrance_seamless", "Météo-France Seamless", "Météo-France"),
    WeatherModel("meteofrance_arpege_world", "Météo-France ARPEGE World", "Météo-France"),
    WeatherModel("meteofrance_arpege_europe", "Météo-France ARPEGE Europe", "Météo-France", True),
    WeatherModel("meteofrance_arome_france", "Météo-France AROME France", "Météo-France", True),
    WeatherModel(
        "meteofrance_arome_france_hd", "Météo-France AROME France HD", "Météo-France", True
    ),
    # ItaliaMeteo
    WeatherModel("italia_meteo_arpae_icon_2i", "ItaliaMeteo ARPAE ICON 2I", "ItaliaMeteo", True),
    # MET Norway
    WeatherModel("metno_seamless", "MET Norway Nordic Seamless (with ECMWF)", "MET Norway"),
    WeatherModel("metno_nordic", "MET Norway Nordic", "MET Norway", True),
    # KNMI
    WeatherModel("knmi_seamless", "KNMI Seamless (with ECMWF)", "KNMI"),
    WeatherModel("knmi_harmonie_arome_europe", "KNMI Harmonie AROME Europe", "KNMI", True),
    WeatherModel(
        "knmi_harmonie_arome_netherlands", "KNMI Harmonie AROME Netherlands", "KNMI", True
    ),
    # DMI
    WeatherModel("dmi_seamless", "DMI Seamless (with ECMWF)", "DMI"),
    WeatherModel("dmi_harmonie_arome_europe", "DMI Harmonie AROME Europe", "DMI", True),
    # UK Met Office
    WeatherModel("ukmo_seamless", "UK Met Office Seamless", "UK Met Office"),
    WeatherModel("ukmo_global_deterministic_10km", "UK Met Office Global 10 km", "UK Met Office"),
    WeatherModel("ukmo_uk_deterministic_2km", "UK Met Office UK 2 km", "UK Met Office", True),
    # MeteoSwiss
    WeatherModel("meteoswiss_icon_seamless", "MeteoSwiss ICON Seamless", "MeteoSwiss", True),
    WeatherModel("meteoswiss_icon_ch1", "MeteoSwiss ICON CH1", "MeteoSwiss", True),
    WeatherModel("meteoswiss_icon_ch2", "MeteoSwiss ICON CH2", "MeteoSwiss", True),
    # GeoSphere Austria
    WeatherModel("geosphere_seamless", "GeoSphere Seamless (with ECMWF)", "GeoSphere Austria"),
    WeatherModel("geosphere_claef_austria", "GeoSphere C-LAEF Austria", "GeoSphere Austria", True),
    # CHMI
    WeatherModel("chmi_aladin_seamless", "CHMI Aladin Seamless", "CHMI"),
    WeatherModel("chmi_aladin_central_europe_2km", "CHMI Aladin Central Europe 2 km", "CHMI", True),
    WeatherModel("chmi_aladin_cz_1km", "CHMI Aladin CZ 1 km", "CHMI", True),
)

MODELS_BY_ID: dict[str, WeatherModel] = {m.id: m for m in MODELS}


def get_model(model_id: str) -> WeatherModel:
    """Model by id; unknown ids (e.g. a model added by Open-Meteo later) still work."""
    return MODELS_BY_ID.get(model_id) or WeatherModel(model_id, model_id, "Open-Meteo")
