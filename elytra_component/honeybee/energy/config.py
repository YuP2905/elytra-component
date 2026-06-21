from __future__ import annotations
from typing import (
    Tuple,
    Dict,
    Iterable,
    cast,
    get_args,
    TYPE_CHECKING,
)
if TYPE_CHECKING:
    from .typing import (
        EfficiencyStandardKeys,
        EfficiencyStandards,
        SolarDistributionKeys,
        SolarDistributionValues,
    )

from .typing import (
    EnergyResultName,
    CoolingExtraOutputName,
    HeatingExtraOutputName,
    HotWaterExtraOutputName,
    FanElectricExtraOutputName,
    PumpElectricExtraOutputName,
    FaceResultName,
    FaceIndoorTempOutputName,
    FaceOutdoorTempOutputName,
    OpaqueEnergyFlowOutputName,
    WindowLossEnergyOutputName,
    WindowGainEnergyOutputName,
    ComfortResultName,
    ZoneOperativeTemperatureOutputName,
    ZoneMeanAirTemperatureOutputName,
    ZoneMeanRadiantTemperatureOutputName,
    ZoneAirRelativeHumidityOutputName,
    ZoneHeatingSetpointNotMetOutputName,
    ZoneCoolingSetpointNotMetOutputName
)


from honeybee_energy.result.loadbalance import LoadBalance


SOLAR_DISTRIBUTIONS: Dict["SolarDistributionKeys", "SolarDistributionValues"] = {
    "0": "MinimalShadowing",
    "1": "FullExterior",
    "2": "FullInteriorAndExterior",
    "3": "FullExteriorWithReflections",
    "4": "FullInteriorAndExteriorWithReflections",
    "MinimalShadowing": "MinimalShadowing",
    "FullExterior": "FullExterior",
    "FullInteriorAndExterior": "FullInteriorAndExterior",
    "FullExteriorWithReflections": "FullExteriorWithReflections",
    "FullInteriorAndExteriorWithReflections": "FullInteriorAndExteriorWithReflections",
}

EFF_STANDARDS: Dict["EfficiencyStandardKeys", "EfficiencyStandards"] = {
    "DOE_Ref_Pre_1980": "DOE_Ref_Pre_1980",
    "DOE_Ref_1980_2004": "DOE_Ref_1980_2004",
    "ASHRAE_2004": "ASHRAE_2004",
    "ASHRAE_2007": "ASHRAE_2007",
    "ASHRAE_2010": "ASHRAE_2010",
    "ASHRAE_2013": "ASHRAE_2013",
    "ASHRAE_2016": "ASHRAE_2016",
    "ASHRAE_2019": "ASHRAE_2019",
    "pre_1980": "DOE_Ref_Pre_1980",
    "1980_2004": "DOE_Ref_1980_2004",
    "2004": "ASHRAE_2004",
    "2007": "ASHRAE_2007",
    "2010": "ASHRAE_2010",
    "2013": "ASHRAE_2013",
    "2016": "ASHRAE_2016",
    "2019": "ASHRAE_2019",
}

def _merge_outputs(
    base_outputs: Iterable[str],
    extra_outputs: Iterable[str],
) -> Tuple[str, ...]:
    """Merge default EnergyPlus output names with extra output names."""
    return tuple((*base_outputs, *extra_outputs))

def _as_outputs(
    names: Iterable[str],
) -> Tuple[str, ...]:
    """Store EnergyPlus output names with a fixed tuple structure."""
    return tuple(names)

COOLING_EXTRA_OUTPUTS = cast(
    Tuple["CoolingExtraOutputName", ...],
    get_args(CoolingExtraOutputName)
)
HEATING_EXTRA_OUTPUTS = cast(
    Tuple["HeatingExtraOutputName", ...],
    get_args(HeatingExtraOutputName)
)
HOT_WATER_EXTRA_OUTPUTS = cast(
    Tuple["HotWaterExtraOutputName", ...],
    get_args(HotWaterExtraOutputName)
)
FAN_ELECTRIC_EXTRA_OUTPUTS = cast(
    Tuple["FanElectricExtraOutputName", ...],
    get_args(FanElectricExtraOutputName)
)
PUMP_ELECTRIC_EXTRA_OUTPUTS = cast(
    Tuple["PumpElectricExtraOutputName", ...],
    get_args(PumpElectricExtraOutputName)
)

ENERGY_OUTPUTS: Dict[
    EnergyResultName,
    Tuple[str, ...]
] = {
    EnergyResultName.COOLING: _merge_outputs(
        LoadBalance.COOLING,
        COOLING_EXTRA_OUTPUTS,
    ),
    EnergyResultName.HEATING: _merge_outputs(
        LoadBalance.HEATING,
        HEATING_EXTRA_OUTPUTS,
    ),
    EnergyResultName.LIGHTING: _as_outputs(LoadBalance.LIGHTING),
    EnergyResultName.ELECTRIC_EQUIP: _as_outputs(LoadBalance.ELECTRIC_EQUIP),
    EnergyResultName.GAS_EQUIP: _as_outputs(LoadBalance.GAS_EQUIP),
    EnergyResultName.PROCESS: _as_outputs(LoadBalance.PROCESS),
    EnergyResultName.HOT_WATER: _merge_outputs(
        LoadBalance.HOT_WATER,
        HOT_WATER_EXTRA_OUTPUTS,
    ),
    EnergyResultName.FAN_ELECTRIC: FAN_ELECTRIC_EXTRA_OUTPUTS,
    EnergyResultName.PUMP_ELECTRIC: PUMP_ELECTRIC_EXTRA_OUTPUTS,
    EnergyResultName.PEOPLE_GAIN: _as_outputs(LoadBalance.PEOPLE_GAIN),
    EnergyResultName.SOLAR_GAIN: _as_outputs(LoadBalance.SOLAR_GAIN),
    EnergyResultName.INFIL_GAIN: _as_outputs(LoadBalance.INFIL_GAIN),
    EnergyResultName.INFIL_LOSS: _as_outputs(LoadBalance.INFIL_LOSS),
    EnergyResultName.VENT_LOSS: _as_outputs(LoadBalance.VENT_LOSS),
    EnergyResultName.VENT_GAIN: _as_outputs(LoadBalance.VENT_GAIN),
    EnergyResultName.NAT_VENT_GAIN: _as_outputs(LoadBalance.NAT_VENT_GAIN),
    EnergyResultName.NAT_VENT_LOSS: _as_outputs(LoadBalance.NAT_VENT_LOSS),
}



FACE_INDOOR_TEMP_OUTPUTS = cast(
    Tuple["FaceIndoorTempOutputName", ...],
    get_args(FaceIndoorTempOutputName)
)
FACE_OUTDOOR_TEMP_OUTPUTS = cast(
    Tuple["FaceOutdoorTempOutputName", ...],
    get_args(FaceOutdoorTempOutputName)
)
OPAQUE_ENERGY_FLOW_OUTPUTS = cast(
    Tuple["OpaqueEnergyFlowOutputName", ...],
    get_args(OpaqueEnergyFlowOutputName)
)
WINDOW_LOSS_ENERGY_OUTPUTS = cast(
    Tuple["WindowLossEnergyOutputName", ...],
    get_args(WindowLossEnergyOutputName)
)
WINDOW_GAIN_ENERGY_OUTPUTS = cast(
    Tuple["WindowGainEnergyOutputName", ...],
    get_args(WindowGainEnergyOutputName)
)

FACE_OUTPUTS: Dict[
    FaceResultName,
    Tuple[str, ...]
] = {
    FaceResultName.FACE_INDOOR_TEMP: FACE_INDOOR_TEMP_OUTPUTS,
    FaceResultName.FACE_OUTDOOR_TEMP: FACE_OUTDOOR_TEMP_OUTPUTS,
}



OPER_TEMP_OUTPUTS = cast(
    Tuple["ZoneOperativeTemperatureOutputName", ...],
    get_args(ZoneOperativeTemperatureOutputName)
)
AIR_TEMP_OUTPUTS = cast(
    Tuple["ZoneMeanAirTemperatureOutputName", ...],
    get_args(ZoneMeanAirTemperatureOutputName)
)
RAD_TEMP_OUTPUTS = cast(
    Tuple["ZoneMeanRadiantTemperatureOutputName", ...],
    get_args(ZoneMeanRadiantTemperatureOutputName)
)
REL_HUMIDITY_OUTPUTS = cast(
    Tuple["ZoneAirRelativeHumidityOutputName", ...],
    get_args(ZoneAirRelativeHumidityOutputName)
)
UNMET_HEAT_OUTPUTS = cast(
    Tuple["ZoneHeatingSetpointNotMetOutputName", ...],
    get_args(ZoneHeatingSetpointNotMetOutputName)
)
UNMET_COOL_OUTPUTS = cast(
    Tuple["ZoneCoolingSetpointNotMetOutputName", ...],
    get_args(ZoneCoolingSetpointNotMetOutputName)
)

COMFORT_OUTPUTS: Dict[
    ComfortResultName,
    Tuple[str, ...]
] = {
    ComfortResultName.OPER_TEMP: OPER_TEMP_OUTPUTS,
    ComfortResultName.AIR_TEMP: AIR_TEMP_OUTPUTS,
    ComfortResultName.RAD_TEMP: RAD_TEMP_OUTPUTS,
    ComfortResultName.REL_HUMIDITY: REL_HUMIDITY_OUTPUTS,
    ComfortResultName.UNMET_HEAT: UNMET_HEAT_OUTPUTS,
    ComfortResultName.UNMET_COOL: UNMET_COOL_OUTPUTS,
}
