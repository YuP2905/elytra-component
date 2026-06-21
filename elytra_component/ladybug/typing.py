from __future__ import annotations
from pathlib import Path
from typing import (
    Literal,
    Optional,
    Tuple,
    Union,
    TYPE_CHECKING,
)
if TYPE_CHECKING:
    from ladybug.datacollection import (
        BaseCollection,
        DailyCollection,
        HourlyContinuousCollection,
        HourlyDiscontinuousCollection,
        MonthlyCollection,
        MonthlyPerHourCollection,
    )
    from ladybug.dt import DateTime
    from ladybug_geometry.geometry2d.pointvector import Point2D, Vector2D
    from ladybug_geometry.geometry3d.pointvector import Point3D, Vector3D

type HeaderMetadataValue = Optional[Union[str, float, int, bool]]

type LadybugDataCollection = Union[
    "DailyCollection",
    "HourlyContinuousCollection",
    "HourlyDiscontinuousCollection",
    "MonthlyCollection",
    "MonthlyPerHourCollection",
]

type HourlyDataCollection = Union[
    "HourlyContinuousCollection",
    "HourlyDiscontinuousCollection",
]

type WeatherFilePaths = Tuple[
    Path,
    Optional[Path],
    Optional[Path],
]

type NumericDataInput = Union["BaseCollection", float, int]

type NumericDataValue = Union["BaseCollection", float, int]

type WindTerrain = Union[
    Literal["city", "suburban", "country", "water"],
    Literal[0, 1, 2, 3],
]

type LadybugPointVector = Union[
    "Point2D",
    "Vector2D",
    "Point3D",
    "Vector3D",
]

type DataDateTimeValue = Union["DateTime", float, int]

type DataInterval = Literal[
    "hourly",
    "monthly",
    "daily",
    "monthly-per-hour",
]

type LadybugColorSetName = Literal[
    "Original Ladybug",
    "Nuanced Ladybug",
    "Multi-colored Ladybug",
    "Ecotect",
    "View Study",
    "Shadow Study",
    "Glare Study",
    "Annual Comfort",
    "Thermal Comfort",
    "Peak Load Balance",
    "Heat Sensation",
    "Cold Sensation",
    "Benefit/Harm",
    "Harm",
    "Benefit",
    "Shade Benefit/Harm",
    "Shade Harm",
    "Shade Benefit",
    "Energy Balance",
    "Energy Balance Storage",
    "THERM",
    "Cloud Cover",
    "Black to White",
    "Blue Green Red",
    "Multicolored 2",
    "Multicolored 3",
    "OpenStudio Palette",
    "Cividis",
    "Viridis",
    "Parula",
]
