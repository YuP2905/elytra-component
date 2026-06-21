from __future__ import annotations

from typing import (
    Optional,
    Tuple,
    cast,
    TYPE_CHECKING,
)

from ladybug.datacollection import (
    BaseCollection,
    HourlyContinuousCollection,
)
from ladybug.datatype.fraction import (
    HumidityRatio,
    RelativeHumidity,
)
from ladybug.datatype.specificenergy import Enthalpy
from ladybug.datatype.temperature import (
    DewPointTemperature,
    HeatIndexTemperature,
    WetBulbGlobeTemperature,
    WetBulbTemperature,
    WindChillTemperature,
)
from ladybug.datatype.temperaturetime import (
    CoolingDegreeTime,
    HeatingDegreeTime,
)
from ladybug.psychrometrics import (
    dew_point_from_db_rh,
    enthalpy_from_db_hr,
    humid_ratio_from_db_rh,
    rel_humid_from_db_dpt,
    wet_bulb_from_db_rh,
)
from ladybug.windprofile import WindProfile
from ladybug_comfort.degreetime import (
    cooling_degree_time,
    heating_degree_time,
)
from ladybug_comfort.hi import heat_index as heat_index_temperature
from ladybug_comfort.wbgt import wet_bulb_globe_temperature
from ladybug_comfort.wc import windchill_temp

if TYPE_CHECKING:
    from ..typing import (
        NumericDataInput,
        NumericDataValue,
        WindTerrain,
    )


def _terrain_name(
    terrain: "WindTerrain",
) -> str:
    """Return the Ladybug terrain name for text or integer terrain input.

    Args:
        terrain: Terrain name or terrain index.

    Returns:
        Ladybug terrain name.
    """
    if isinstance(terrain, int):
        terrain_names = (
            "city",
            "suburban",
            "country",
            "water",
        )
        if terrain < 0 or terrain >= len(terrain_names):
            raise ValueError(
                "Terrain integer must be 0, 1, 2, or 3."
            )
        return terrain_names[terrain]

    return terrain


def degree_days(
    dry_bulb: BaseCollection,
    heat_base: float = 18.0,
    cool_base: float = 23.0,
) -> Tuple[BaseCollection, BaseCollection, float, float]:
    """Calculate heating and cooling degree-days.

    Source component: `LB Degree Days.py`.

    Args:
        dry_bulb: Outdoor dry bulb temperature collection in C.
        heat_base: Base temperature below which an hour is heating mode.
        cool_base: Base temperature above which an hour is cooling mode.

    Returns:
        A tuple containing:
        - hourly_heat: Heating degree-day collection.
        - hourly_cool: Cooling degree-day collection.
        - heat_deg_days: Total heating degree-days.
        - cool_deg_days: Total cooling degree-days.
    """
    hourly_heat = HourlyContinuousCollection.compute_function_aligned(
        heating_degree_time,
        [
            dry_bulb,
            heat_base,
        ],
        HeatingDegreeTime(),
        "degC-hours",
    )
    hourly_heat = cast(HourlyContinuousCollection, hourly_heat)
    hourly_heat.convert_to_unit("degC-days")

    hourly_cool = HourlyContinuousCollection.compute_function_aligned(
        cooling_degree_time,
        [
            dry_bulb,
            cool_base,
        ],
        CoolingDegreeTime(),
        "degC-hours",
    )
    hourly_cool = cast(HourlyContinuousCollection, hourly_cool)
    hourly_cool.convert_to_unit("degC-days")

    return (
        hourly_heat,
        hourly_cool,
        float(hourly_heat.total),
        float(hourly_cool.total),
    )


def humidity_metrics(
    dry_bulb: "NumericDataInput",
    rel_humid: "NumericDataInput",
    pressure: "NumericDataInput" = 101325,
) -> Tuple[
    "NumericDataValue",
    "NumericDataValue",
    "NumericDataValue",
    "NumericDataValue",
]:
    """Calculate humidity ratio, enthalpy, wet bulb, and dew point.

    Source component: `LB Humidity Metrics.py`.

    Args:
        dry_bulb: Dry bulb temperature in C.
        rel_humid: Relative humidity in percent.
        pressure: Atmospheric pressure in Pa.

    Returns:
        A tuple containing:
        - humid_ratio: Humidity ratio in kg water / kg air.
        - enthalpy: Enthalpy in kJ/kg.
        - wet_bulb: Wet bulb temperature in C.
        - dew_point: Dew point temperature in C.
    """
    humid_ratio = HourlyContinuousCollection.compute_function_aligned(
        humid_ratio_from_db_rh,
        [
            dry_bulb,
            rel_humid,
            pressure,
        ],
        HumidityRatio(),
        "fraction",
    )
    enthalpy = HourlyContinuousCollection.compute_function_aligned(
        enthalpy_from_db_hr,
        [
            dry_bulb,
            humid_ratio,
        ],
        Enthalpy(),
        "kJ/kg",
    )
    wet_bulb = HourlyContinuousCollection.compute_function_aligned(
        wet_bulb_from_db_rh,
        [
            dry_bulb,
            rel_humid,
            pressure,
        ],
        WetBulbTemperature(),
        "C",
    )
    dew_point = HourlyContinuousCollection.compute_function_aligned(
        dew_point_from_db_rh,
        [
            dry_bulb,
            rel_humid,
        ],
        DewPointTemperature(),
        "C",
    )

    return (
        humid_ratio,
        enthalpy,
        wet_bulb,
        dew_point,
    )


def relative_humidity_from_dew_point(
    dry_bulb: "NumericDataInput",
    dew_point: "NumericDataInput",
) -> "NumericDataValue":
    """Calculate relative humidity from dry bulb and dew point temperature.

    Args:
        dry_bulb: Dry bulb temperature in C.
        dew_point: Dew point temperature in C.

    Returns:
        Relative humidity in percent as a scalar or Ladybug collection.
    """
    return cast(
        "NumericDataValue",
        HourlyContinuousCollection.compute_function_aligned(
            rel_humid_from_db_dpt,
            [
                dry_bulb,
                dew_point,
            ],
            RelativeHumidity(),
            "%",
        ),
    )


def thermal_indices(
    air_temp: "NumericDataInput",
    rel_humid: "NumericDataInput",
    wind_vel: "NumericDataInput",
    mrt: Optional["NumericDataInput"] = None,
) -> Tuple[
    "NumericDataValue",
    "NumericDataValue",
    "NumericDataValue",
]:
    """Calculate WBGT, heat index, and wind chill temperature.

    Source component: `LB Thermal Indices.py`.

    Args:
        air_temp: Air temperature in C.
        rel_humid: Relative humidity in percent.
        wind_vel: Meteorological wind velocity at 10 m in m/s.
        mrt: Mean radiant temperature in C. Defaults to `air_temp`.

    Returns:
        A tuple containing:
        - wbgt: Wet Bulb Globe Temperature in C.
        - heat_index: Heat Index temperature in C.
        - wind_chill: Wind Chill temperature in C.
    """
    mean_radiant_temperature = air_temp if mrt is None else mrt
    wbgt = HourlyContinuousCollection.compute_function_aligned(
        wet_bulb_globe_temperature,
        [
            air_temp,
            mean_radiant_temperature,
            wind_vel,
            rel_humid,
        ],
        WetBulbGlobeTemperature(),
        "C",
    )
    heat_index = HourlyContinuousCollection.compute_function_aligned(
        heat_index_temperature,
        [
            air_temp,
            rel_humid,
        ],
        HeatIndexTemperature(),
        "C",
    )
    wind_chill = HourlyContinuousCollection.compute_function_aligned(
        windchill_temp,
        [
            air_temp,
            wind_vel,
        ],
        WindChillTemperature(),
        "C",
    )

    return (
        wbgt,
        heat_index,
        wind_chill,
    )


def wind_speed(
    met_wind_vel: "NumericDataInput",
    height: float = 1.0,
    terrain: "WindTerrain" = "city",
    met_height: float = 10.0,
    met_terrain: "WindTerrain" = "country",
    log_law: bool = False,
) -> "NumericDataValue":
    """Calculate wind speed at a height above the ground.

    Source component: `LB Wind Speed.py`.

    Args:
        met_wind_vel: Meteorological wind speed measured at `met_height`.
        height: Target height above ground in meters.
        terrain: Target terrain type.
        met_height: Meteorological measurement height in meters.
        met_terrain: Meteorological terrain type.
        log_law: Use logarithmic wind profile instead of the power law.

    Returns:
        Air speed at the requested height as a scalar or Ladybug collection.
    """
    profile = WindProfile(
        _terrain_name(terrain),
        _terrain_name(met_terrain),
        met_height,  # pyright: ignore[reportArgumentType]
        log_law,
    )
    if isinstance(met_wind_vel, BaseCollection):
        return profile.calculate_wind_data(
            met_wind_vel,
            height,  # pyright: ignore[reportArgumentType]
        )

    return profile.calculate_wind(
        float(met_wind_vel),
        height,  # pyright: ignore[reportArgumentType]
    )
