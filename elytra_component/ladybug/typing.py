from __future__ import annotations
from typing import (
    Union,
    Literal,
)
from ladybug.datacollection import (
    DailyCollection,
    HourlyContinuousCollection,
    HourlyDiscontinuousCollection,
    MonthlyCollection,
    MonthlyPerHourCollection,
)

type LadybugDataCollection = Union[
    DailyCollection,
    HourlyContinuousCollection,
    HourlyDiscontinuousCollection,
    MonthlyCollection,
    MonthlyPerHourCollection,
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