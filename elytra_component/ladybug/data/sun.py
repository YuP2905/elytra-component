from __future__ import annotations
from typing import (
    List,
    Optional,
    Sequence,
    Tuple,
    cast,
    TYPE_CHECKING,
)

from ladybug.sunpath import Sunpath
import numpy as np

if TYPE_CHECKING:
    from ladybug.analysisperiod import AnalysisPeriod
    from ladybug.dt import DateTime
    from ladybug.location import Location
    from ladybug.sunpath import Sun
    from ladybug_geometry.geometry3d.arc import Arc3D
    from ladybug_geometry.geometry3d.pointvector import Point3D, Vector3D
    from ladybug_geometry.geometry3d.polyline import Polyline3D
    from numpy.typing import NDArray


def create_sunpath(
    location: "Location",
    north: float = 0.0,
    dl_saving: Optional["AnalysisPeriod"] = None,
) -> Sunpath:
    """Create a Ladybug Sunpath from a Ladybug location."""
    return Sunpath.from_location(
        location,
        cast(int, north),
        dl_saving,
    )


def get_suns(
    sunpath: Sunpath,
    hoys: Sequence[float | int],
    solar_time: bool = False,
) -> Tuple["Sun", ...]:
    """Calculate daytime suns for hours of year."""
    suns: List["Sun"] = []
    for hoy in hoys:
        sun = sunpath.calculate_sun_from_hoy(
            hoy,
            solar_time,
        )
        if sun.is_during_day:
            suns.append(sun)

    return tuple(suns)


def get_sun_vectors(
    suns: Sequence["Sun"],
) -> Tuple["Vector3D", ...]:
    """Return Ladybug sun vectors from suns."""
    return tuple(
        sun.sun_vector
        for sun in suns
    )


def get_sun_datetimes(
    suns: Sequence["Sun"],
) -> Tuple["DateTime", ...]:
    """Return Ladybug datetimes from suns."""
    return tuple(
        cast("DateTime", sun.datetime)
        for sun in suns
    )


def get_sunpath_polylines(
    sunpath: Sunpath,
    steps_per_month: int = 10,
    solar_time: bool = False,
) -> Tuple["Polyline3D", ...]:
    """Return hourly analemma polylines for a sunpath."""
    if steps_per_month < 1 or steps_per_month > 28:
        raise ValueError(
            "The steps_per_month must be between 1 and 28."
        )

    return tuple(
        cast("Polyline3D", polyline)
        for polyline in sunpath.hourly_analemma_polyline3d(
            is_solar_time=solar_time,
            steps_per_month=steps_per_month,
        )
    )


def get_sunpath_arcs(
    sunpath: Sunpath,
    daily: bool = False,
    datetimes: Optional[Sequence["DateTime"]] = None,
) -> Tuple["Arc3D", ...]:
    """Return monthly or selected daily sunpath arcs."""
    if daily and datetimes is None:
        raise ValueError(
            "If daily is True, datetimes must be provided."
        )

    if daily and datetimes is not None:
        dates = sorted(
            {
                (dt.month, dt.day)
                for dt in datetimes
            }
        )
        return tuple(
            cast(
                "Arc3D",
                sunpath.day_arc3d(
                    month,
                    day,
                ),
            )
            for month, day in dates
        )

    return tuple(
        cast(
            "Arc3D",
            arc,
        )
        for arc in sunpath.monthly_day_arc3d()
    )


def get_sun_points(
    suns: Sequence["Sun"],
) -> Tuple["Point3D", ...]:
    """Return 3D positions for suns."""
    return tuple(
        sun.position_3d()
        for sun in suns
    )


def get_sun_altitudes_azimuths(
    suns: Sequence["Sun"],
) -> "NDArray[np.float64]":
    """Return a ``(2, n)`` array ordered as altitude and azimuth."""
    altitude_azimuth: List[Tuple[float, float]] = []
    for sun in suns:
        altitude_azimuth.append(
            (
                sun.altitude,
                sun.azimuth,
            )
        )

    return np.asarray(
        altitude_azimuth,
        dtype=np.float64,
    ).T
