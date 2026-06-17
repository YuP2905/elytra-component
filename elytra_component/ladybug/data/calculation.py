from __future__ import annotations
from typing import (
    List,
    Tuple,
    Union,
    Sequence,
    Optional,
    Generator,
    cast,
    TYPE_CHECKING,
)
if TYPE_CHECKING:
    from ladybug.sunpath import Sun
    from ladybug.dt import DateTime
    from ladybug.location import Location
    from ladybug.analysisperiod import AnalysisPeriod
    from ladybug_geometry.geometry3d.arc import Arc3D
    from ladybug_geometry.geometry3d.polyline import Polyline3D
    from ladybug_geometry.geometry3d.pointvector import Vector3D, Point3D
    from numpy.typing import NDArray

from ladybug.sunpath import Sunpath
from ladybug.datacollection import (
    BaseCollection,
    HourlyContinuousCollection,
    HourlyDiscontinuousCollection,
)
import numpy as np

def create_sunpath(
    location: "Location",
    north: float = 0.0,
    dl_saving: Optional["AnalysisPeriod"] = None,
) -> Sunpath:
    return Sunpath.from_location(
        location,
        north,
        dl_saving
    )

def get_suns(
    sunpath: Sunpath,
    hoys: Sequence[float | int],
    solar_time: bool = False,
) -> Tuple["Sun", ...]:
    suns: List["Sun"] = []
    for hoy in hoys:
        sun = sunpath.calculate_sun_from_hoy(
            hoy,
            solar_time
        )
        if sun.is_during_day:
            suns.append(sun)

    return tuple(suns)

def get_sun_vectors(
    suns: Sequence["Sun"],
) -> Tuple["Vector3D", ...]:

    return tuple(
        sun.sun_vector
        for sun in suns
    )

def get_sun_datetimes(
    suns: Sequence["Sun"],
) -> Tuple["DateTime", ...]:

    return tuple(
        cast("DateTime", sun.datetime)
        for sun in suns
    )

def get_sunpath_polylines(
    sunpath: Sunpath,
    steps_per_month: int = 32,
    solar_time: bool = False,
) -> Tuple["Polyline3D", ...]:
    sun_polylines = tuple(
        cast("Polyline3D", p_l)
        for p_l in sunpath.hourly_analemma_polyline3d(
            is_solar_time=solar_time,
            steps_per_month=steps_per_month,
        )
    )
    return sun_polylines

def get_sunpath_arcs(
    sunpath: Sunpath,
    daily: bool = False,
    datetimes: Optional[Sequence["DateTime"]] = None,
):
    if daily and datetimes is None:
        raise ValueError(
            "If daily is True, datetimes must be provided."
        )

    if datetimes is not None:
        dates = sorted(
            {
                (dt.month, dt.day)
                for dt in datetimes
            }
        )

    sun_arcs = tuple(
        cast(
            "Arc3D",
            sunpath.day_arc3d(
                m,
                d,
            ),
        )
        for m, d in dates
    ) if daily and datetimes is not None else tuple(
        cast(
            "Arc3D",
            arc
        )
        for arc in sunpath.monthly_day_arc3d()
    )
    return sun_arcs


def get_sun_points(
    suns: Sequence["Sun"],
) -> Tuple["Point3D", ...]:

    points: List["Point3D"] = []
    for sun in suns:
        points.append(sun.position_3d())

    return tuple(points)

def get_sun_altitudes_azimuths(
    suns: Sequence["Sun"],
) -> "NDArray[np.float64]":

    al_az : List[Tuple[float, float]] = []
    for sun in suns:
        al_az.append((sun.altitude, sun.azimuth))

    return np.asarray(
        al_az,
        dtype= np.float64
    ).T # shape (2, n): altitude, azimuth

def filter_data_collection_by_statement(
    data: Union["BaseCollection", Sequence["BaseCollection"]],
    statement: str,
) -> Union["BaseCollection", Sequence["BaseCollection"]]:
    data = (data,) if isinstance(data, BaseCollection) else data

    filtered_data: List["BaseCollection"] = BaseCollection.filter_collections_by_statement(
        data,
        statement,
    )

    return filtered_data[0] if len(filtered_data) == 1 else tuple(filtered_data)

def align_hoys_by_hourly_data_collection(
    hoys: Sequence[float | int] | float | int,
    data: Union[
        "HourlyContinuousCollection", "HourlyDiscontinuousCollection",
        Sequence[Union["HourlyContinuousCollection", "HourlyDiscontinuousCollection"]]
    ],
) -> "NDArray[np.float64]":
    hoys = (hoys,) if isinstance(hoys, (float, int)) else hoys
    data = (data,) if isinstance(data, (HourlyContinuousCollection, HourlyDiscontinuousCollection)) else data

    first_data = data[0]
    if len(data) > 1:
        is_aligned = all(
            first_data.is_collection_aligned(d) for d in data[1:]
        )

        if not is_aligned:
            raise ValueError(
                "The data collections are not aligned."
            )

    data_hoys = {
        cast("DateTime", dt).hoy
        for dt in first_data.datetimes
    }

    aligned_hoys = tuple(
        h
        for h in hoys
        if h in data_hoys
    )

    return np.asarray(
        aligned_hoys,
        dtype= np.float64
    ) # shape (n,) where n is the number of aligned hoys

def align_hourly_data_collection_by_suns(
    data: Union[
        "HourlyContinuousCollection", "HourlyDiscontinuousCollection",
        Sequence[Union["HourlyContinuousCollection", "HourlyDiscontinuousCollection"]]
    ],
    suns: Sequence["Sun"],
) -> Union[
    "HourlyContinuousCollection", "HourlyDiscontinuousCollection",
    Tuple[Union["HourlyContinuousCollection", "HourlyDiscontinuousCollection"], ...]
]:
    data = (data,) if isinstance(data, (HourlyContinuousCollection, HourlyDiscontinuousCollection)) else data

    sun_moys = tuple(
        cast("DateTime", sun.datetime).moy
        for sun in suns
    )

    aligned_data: List[Union["HourlyContinuousCollection", "HourlyDiscontinuousCollection"]] = []
    for d in data:
        d= cast(
            Union["HourlyContinuousCollection", "HourlyDiscontinuousCollection"],
            d
        )
        aligned_data.append(
            d.filter_by_moys(sun_moys)
        )

    return aligned_data[0] if len(aligned_data) == 1 else tuple(aligned_data)
