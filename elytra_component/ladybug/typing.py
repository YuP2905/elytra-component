from __future__ import annotations
from pathlib import Path
from typing import (
    Protocol,
    Tuple,
    Union,
    Literal,
    TYPE_CHECKING,
)
from ladybug.datacollection import (
    DailyCollection,
    HourlyContinuousCollection,
    HourlyDiscontinuousCollection,
    MonthlyCollection,
    MonthlyPerHourCollection,
)
from ladybug.dt import DateTime
from ladybug_geometry.geometry2d.pointvector import Point2D, Vector2D
from ladybug_geometry.geometry3d.pointvector import Point3D, Vector3D

if TYPE_CHECKING:
    from matplotlib.text import Text


class MatplotlibTextMethod(Protocol):
    """Callable interface shared by 2D and 3D matplotlib text methods."""

    def __call__(
        self,
        *args: Union[float, str],
        **kwargs: object,
    ) -> "Text":
        ...

type LadybugDataCollection = Union[
    DailyCollection,
    HourlyContinuousCollection,
    HourlyDiscontinuousCollection,
    MonthlyCollection,
    MonthlyPerHourCollection,
]

type HourlyDataCollection = Union[
    HourlyContinuousCollection,
    HourlyDiscontinuousCollection,
]

type WeatherFilePaths = Tuple[
    Path,
    Union[Path, None],
    Union[Path, None],
]

type MatplotlibColor = Union[
    str,
    Tuple[float, float, float],
    Tuple[float, float, float, float],
]

type ColorbarOrientation = Literal[
    "horizontal",
    "vertical",
]

type MatplotlibTickAxis = Literal[
    "x",
    "y",
]

type LadybugPointVector = Union[
    Point2D,
    Vector2D,
    Point3D,
    Vector3D,
]

type DataDateTimeValue = Union[
    DateTime,
    float,
    int,
]

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
