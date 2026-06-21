from __future__ import annotations
from typing import (
    List,
    Union,
    Dict,
    Literal,
    Mapping,
    Optional,
    TypedDict,
    TYPE_CHECKING,
)
if TYPE_CHECKING:
    from numpy.typing import NDArray
    from ladybug.datacollection import (
        DailyCollection,
        HourlyContinuousCollection,
        MonthlyCollection,
    )


from pathlib import Path
from enum import StrEnum
import numpy as np

type MeasureArgumentValue = Union[str, int, float, bool]
type MeasureArgumentValues = Mapping[str, MeasureArgumentValue]

type LoadType = Literal[
    "All",
    "Total",
    "Sensible",
    "Latent",
]
type ReportFrequency = Literal[
    "Annual",
    "Monthly",
    "Daily",
    "Hourly",
    "Timestep",
]
type TerrainValues = Literal["Ocean", "Country", "Suburbs", "City", "Urban"]

type EfficiencyStandards = Literal[
    "DOE_Ref_Pre_1980",
    "DOE_Ref_1980_2004",
    "ASHRAE_2004",
    "ASHRAE_2007",
    "ASHRAE_2010",
    "ASHRAE_2013",
    "ASHRAE_2016",
    "ASHRAE_2019",
]

type EfficiencyStandardKeys = Literal[
    # "DOE_Ref_Pre_1980",
    # "DOE_Ref_1980_2004",
    # "ASHRAE_2004",
    # "ASHRAE_2007",
    # "ASHRAE_2010",
    # "ASHRAE_2013",
    # "ASHRAE_2016",
    # "ASHRAE_2019",
    EfficiencyStandards,
    "pre_1980",
    "1980_2004",
    "2004",
    "2007",
    "2010",
    "2013",
    "2016",
    "2019",
]


type SolarDistributionKeys = Literal[
    "0",
    "1",
    "2",
    "3",
    "4",
    "MinimalShadowing",
    "FullExterior",
    "FullInteriorAndExterior",
    "FullExteriorWithReflections",
    "FullInteriorAndExteriorWithReflections",
]


type SolarDistributionValues = Literal[
    "MinimalShadowing",
    "FullExterior",
    "FullInteriorAndExterior",
    "FullExteriorWithReflections",
    "FullInteriorAndExteriorWithReflections",
]

type CalculationMethod = Literal[
    "PolygonClipping",
    "PixelCounting",
]

type UpdateMethod = Literal[
    "Periodic",
    "Timestep",
]


class SimulationFiles(TypedDict):
    osm: Path
    osw: Optional[Path]
    idf: Optional[Path]
    sim_params: Optional[Path]

class EnergySimulationResult(TypedDict):
    osm: Path
    idf: Path
    sql: Path
    zsz: Optional[Path]
    rdd: Optional[Path]
    html: Optional[Path]
    err: Optional[Path]

class RunIDFResult(TypedDict):
    sql: Path
    zsz: Optional[Path]
    rdd: Optional[Path]
    html: Optional[Path]

class RunOSWResult(TypedDict):
    osm: Path
    idf: Path
    sql: Path
    zsz: Optional[Path]
    rdd: Optional[Path]
    html: Optional[Path]


class RunOSMResult(TypedDict):
    idf: Path
    sql: Path
    zsz: Optional[Path]
    rdd: Optional[Path]
    html: Optional[Path]


class EnergyResultName(StrEnum):
    COOLING = "cooling"
    HEATING = "heating"
    LIGHTING = "lighting"
    ELECTRIC_EQUIP = "electric_equip"
    GAS_EQUIP = "gas_equip"
    PROCESS = "process"
    HOT_WATER = "hot_water"
    FAN_ELECTRIC = "fan_electric"
    PUMP_ELECTRIC = "pump_electric"
    PEOPLE_GAIN = "people_gain"
    SOLAR_GAIN = "solar_gain"
    INFIL_GAIN = "infil_gain"
    INFIL_LOSS = "infil_loss"
    VENT_LOSS = "vent_loss"
    VENT_GAIN = "vent_gain"
    NAT_VENT_GAIN = "nat_vent_gain"
    NAT_VENT_LOSS = "nat_vent_loss"

type CoolingExtraOutputName = Literal[
    "Cooling Coil Electricity Energy",
    "Chiller Electricity Energy",
    "Zone VRF Air Terminal Cooling Electricity Energy",
    "VRF Heat Pump Cooling Electricity Energy",
    "Chiller Heater System Cooling Electricity Energy",
    "District Cooling Water Energy",
    "Evaporative Cooler Electricity Energy",
]

type HeatingExtraOutputName = Literal[
    "Boiler NaturalGas Energy",
    "Heating Coil Total Heating Energy",
    "Heating Coil NaturalGas Energy",
    "Heating Coil Electricity Energy",
    "Humidifier Electricity Energy",
    "Zone VRF Air Terminal Heating Electricity Energy",
    "VRF Heat Pump Heating Electricity Energy",
    "VRF Heat Pump Defrost Electricity Energy",
    "Chiller Heater System Heating Electricity Energy",
    "District Heating Water Energy",
    "Baseboard Electricity Energy",
    "Hot_Water_Loop_Central_Air_Source_Heat_Pump Electricity Consumption",
    "Boiler Electricity Energy",
    "Water Heater NaturalGas Energy",
    "Water Heater Electricity Energy",
    "Cooling Coil Water Heating Electricity Energy",
]
type HotWaterExtraOutputName = Literal[
    "Water Use Equipment Heating Energy",
]
type FanElectricExtraOutputName = Literal[
    "Zone Ventilation Fan Electricity Energy",
    "Fan Electricity Energy",
    "Cooling Tower Fan Electricity Energy",
]
type PumpElectricExtraOutputName = Literal[
    "Pump Electricity Energy",
]


class FaceResultName(StrEnum):
    FACE_INDOOR_TEMP = "face_indoor_temp"
    FACE_OUTDOOR_TEMP = "face_outdoor_temp"
    FACE_ENERGY_FLOW = "face_energy_flow"

type FaceIndoorTempOutputName = Literal[
    "Surface Inside Face Temperature",
]
type FaceOutdoorTempOutputName = Literal[
    "Surface Outside Face Temperature",
]
type OpaqueEnergyFlowOutputName = Literal[
    "Surface Inside Face Conduction Heat Transfer Energy",
]
type WindowLossEnergyOutputName = Literal[
    "Surface Window Heat Loss Energy",
]
type WindowGainEnergyOutputName = Literal[
    "Surface Window Heat Gain Energy",
]


class ComfortResultName(StrEnum):
    OPER_TEMP = "oper_temp"
    AIR_TEMP = "air_temp"
    RAD_TEMP = "rad_temp"
    REL_HUMIDITY = "rel_humidity"
    UNMET_HEAT = "unmet_heat"
    UNMET_COOL = "unmet_cool"

type ZoneOperativeTemperatureOutputName = Literal[
    "Zone Operative Temperature",
]
type ZoneMeanAirTemperatureOutputName = Literal[
    "Zone Mean Air Temperature",
]
type ZoneMeanRadiantTemperatureOutputName = Literal[
    "Zone Mean Radiant Temperature",
]
type ZoneAirRelativeHumidityOutputName = Literal[
    "Zone Air Relative Humidity",
]
type ZoneHeatingSetpointNotMetOutputName = Literal[
    "Zone Heating Setpoint Not Met Time",
]
type ZoneCoolingSetpointNotMetOutputName = Literal[
    "Zone Cooling Setpoint Not Met Time",
]


type EnergyDataCollection = Union[
    "DailyCollection",
    "HourlyContinuousCollection",
    "MonthlyCollection",
]

type SqlResultItem = Union[
    float,
    EnergyDataCollection,
]
type SqlResultList = List[SqlResultItem]

type EnergyOutputResult = Union[
    "NDArray[np.float32]",
    List[EnergyDataCollection],
]

type EnergyResultMap = Dict[
    EnergyResultName,
    EnergyOutputResult,
]

type FaceResultMap = Dict[
    FaceResultName,
    EnergyOutputResult,
]

type ComfortResultMap = Dict[
    ComfortResultName,
    EnergyOutputResult,
]

type EUIEndUses = Mapping[str, float]

class EUIResult(TypedDict):
    eui: float
    total_floor_area: float
    conditioned_floor_area: float
    total_energy: float
    end_uses: EUIEndUses
