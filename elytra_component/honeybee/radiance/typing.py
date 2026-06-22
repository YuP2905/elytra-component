from __future__ import annotations

from pathlib import Path
from os import PathLike
from typing import (
    Dict,
    List,
    Literal,
    NotRequired,
    Sequence,
    Tuple,
    TypedDict,
    Union,
    TYPE_CHECKING,
)

import numpy as np
from numpy.typing import NDArray

if TYPE_CHECKING:
    from honeybee_energy.schedule.fixedinterval import ScheduleFixedInterval
    from honeybee_energy.schedule.ruleset import ScheduleRuleset
    from honeybee_radiance.lightsource.sky import (
        CIE,
        ClimateBased,
        CertainIrradiance,
    )
    from ladybug.datacollection import HourlyContinuousCollection
    from ladybug.wea import Wea


type RecipeType = Literal[
    "0",
    "1",
    "2",
    "rtrace",
    "rpict",
    "rfluxmtx",
    "point-in-time-grid",
    "point-in-time-image",
    "daylight-factor",
    "annual",
]

type DetailLevel = Literal[
    "0",
    "1",
    "2",
    "low",
    "medium",
    "high",
]

type RadianceOptionValue = Union[int, float]
type RadianceOptionTuple = Tuple[
    RadianceOptionValue,
    RadianceOptionValue,
    RadianceOptionValue,
]
type RadianceOptionValues = Dict[str, RadianceOptionValue]
type AnnualResultFiles = List[Path]
type ScheduleInput = Union[
    Sequence[float],
    NDArray[np.float32],
    NDArray[np.float64],
    str,
    PathLike[str],
    "HourlyContinuousCollection",
    "ScheduleRuleset",
    "ScheduleFixedInterval",
]
type SimulationScheduleInput = Union[
    str,
    PathLike[str],
    "HourlyContinuousCollection",
    "ScheduleRuleset",
    "ScheduleFixedInterval",
]
type WeaInput = Union[
    str,
    PathLike[str],
    "Wea",
]
type SkyInput = Union[
    str,
    "CIE",
    "ClimateBased",
    "CertainIrradiance",
]
type PointInTimeMetric = Union[
    Literal[0],
    Literal[1],
    Literal[2],
    Literal[3],
    Literal["0"],
    Literal["1"],
    Literal["2"],
    Literal["3"],
    Literal["illuminance"],
    Literal["irradiance"],
    Literal["luminance"],
    Literal["radiance"],
]
type IrradianceOutputType = Literal[
    "solar",
    "visible",
]


class AnnualGroupResult(TypedDict):
    light_path: str
    identifier: str
    folder: Path
    total_dir: Path
    direct_dir: Path
    total_npy: AnnualResultFiles
    direct_npy: AnnualResultFiles


class AnnualResult(TypedDict):
    project_folder: Path
    simulation_folder: Path
    results: Path
    metrics: Path
    aperture_groups: Dict[str, AnnualGroupResult]


class AnnualGridData(TypedDict):
    total: Dict[str, NDArray[np.float32]]
    direct: Dict[str, NDArray[np.float32]]


class PitResult(TypedDict):
    project_folder: Path
    simulation_folder: Path
    results: List[Path]
    grids_info: List[Path]
    result_files: Dict[str, Path]


class DaylightFactorResult(TypedDict):
    project_folder: Path
    simulation_folder: Path
    results: Path


class AnnualIrradianceResult(TypedDict):
    project_folder: Path
    simulation_folder: Path
    results: Path
    results_direct: Path
    average_irradiance: Path
    peak_irradiance: Path
    cumulative_radiation: Path


class CumulativeRadiationResult(TypedDict):
    project_folder: Path
    simulation_folder: Path
    average_irradiance: Path
    cumulative_radiation: Path


class DirectSunHoursResult(TypedDict):
    project_folder: Path
    simulation_folder: Path
    direct_sun_hours: Path
    cumulative_sun_hours: Path


class SensorGridInfo(TypedDict, total=False):
    full_id: str
    identifier: str
    count: int
    start_ln: NotRequired[int]


class DaylightMetrics(TypedDict):
    da: List[float]
    cda: List[float]
    udi: List[float]
    udi_lower: List[float]
    udi_upper: List[float]
    ase_hours: List[float]
    sda: float
    ase: float


type GridMetrics = Dict[str, DaylightMetrics]
type AnnualMetrics = Dict[str, GridMetrics]
type AnnualRawResults = Dict[str, AnnualGridData]
type AnnualMetricResults = Dict[str, Dict[str, NDArray[np.float32]]]
