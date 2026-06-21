from __future__ import annotations
from typing import (
    Optional,
    Sequence,
    TYPE_CHECKING,
    Union,
)
if TYPE_CHECKING:
    from os import PathLike
    from ladybug.location import Location

from honeybee_radiance.lightsource.sky import (
    CIE,
    ClimateBased,
    CertainIrradiance,
)
from ladybug.wea import Wea
from pathlib import Path


def wea_from_epw(
    epw_file: Union[str, "PathLike[str]"],
    hoys: Optional[Union[int, float, Sequence[int], Sequence[float]]] = None,
    timestep: int = 1,
) -> Wea:
    """Create a Ladybug WEA object from an EPW file.

    Args:
        epw_file: EPW weather file.
        hoys: Optional hours of year used to filter the WEA.
        timestep: Number of timesteps per hour.

    Returns:
        A Ladybug WEA object.
    """
    epw = Path(epw_file)
    if not epw.exists() or epw.suffix.lower() != ".epw":
        raise FileNotFoundError(
            f"EPW file '{epw_file}' does not exist or is not a valid EPW file."
        )
    hoys = (hoys,) if isinstance(hoys, (int, float)) else hoys

    wea = Wea.from_epw_file(
        epw_file,
        timestep,
    )
    if hoys is not None and len(hoys) > 0:
        wea = wea.filter_by_hoys(hoys)

    return wea


def cie_sky(
    location: "Location",
    month: int,
    day: int,
    hour: float,
    sky_type: int = 0,
    north: float = 0.0,
) -> CIE:
    """Create a point-in-time standard Radiance CIE sky.

    Args:
        location: Ladybug Location used to set the sun position.
        month: Month of the year.
        day: Day of the month.
        hour: Hour of the day.
        sky_type: CIE sky type. Defaults to sunny sky with sun.
        north: North angle in degrees.

    Returns:
        A Honeybee CIE sky for point-in-time recipes.
    """
    return CIE.from_location(
        location,
        month,
        day,
        hour,
        sky_type,
        north,  # pyright: ignore[reportArgumentType]
    )


def climatebased_sky(
    wea: Wea,
    month: int,
    day: int,
    hour: float,
    north: float = 0.0,
    colored: bool = False,
) -> ClimateBased:
    """Create a point-in-time climate-based sky from a Wea.

    Args:
        wea: Ladybug Wea used to obtain direct and diffuse irradiance.
        month: Month of the year.
        day: Day of the month.
        hour: Hour of the day.
        north: North angle in degrees.
        colored: Whether the sky is rendered in full color.

    Returns:
        A Honeybee climate-based sky for point-in-time recipes.
    """
    return ClimateBased.from_wea(
        wea,
        month,
        day,
        hour,
        north,  # pyright: ignore[reportArgumentType]
        is_colored=colored,
    )


def custom_sky(
    location: "Location",
    dir_rad: float,
    diff_rad: float,
    month: int,
    day: int,
    hour: float,
    north: float = 0.0,
    colored: bool = False,
) -> ClimateBased:
    """Create a custom sky from direct and diffuse irradiance.

    Args:
        location: Ladybug Location used to set the sun position.
        dir_rad: Direct normal irradiance in W/m2.
        diff_rad: Diffuse horizontal irradiance in W/m2.
        month: Month of the year.
        day: Day of the month.
        hour: Hour of the day.
        north: North angle in degrees.
        colored: Whether the sky is rendered in full color.

    Returns:
        A Honeybee climate-based sky for point-in-time recipes.
    """
    return ClimateBased.from_location(
        location,
        month,
        day,
        hour,
        dir_rad,
        diff_rad,
        north,  # pyright: ignore[reportArgumentType]
        is_colored=colored,
    )


def certain_illuminance(
    value: float = 10000.0,
) -> CertainIrradiance:
    """Create a uniform sky that yields a certain illuminance.

    Args:
        value: Desired sky horizontal illuminance in lux.

    Returns:
        A Honeybee sky for point-in-time recipes.
    """
    return CertainIrradiance.from_illuminance(
        value,  # pyright: ignore[reportArgumentType]
    )
