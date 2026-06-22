from __future__ import annotations
from typing import (
    Union,
    Sequence,
    Literal,
    Optional,
    cast,
    TYPE_CHECKING,
)
if TYPE_CHECKING:
    from os import PathLike
    from ladybug.analysisperiod import AnalysisPeriod
    from honeybee_energy.measure import MeasureArgument
    from ..typing import (
        LoadType,
        ReportFrequency,
        SolarDistributionKeys,
        EfficiencyStandardKeys,
        CalculationMethod,
        UpdateMethod,
        TerrainValues,
        MeasureArgumentValues,
    )

from honeybee_energy.measure import Measure
from honeybee_energy.simulation.control import SimulationControl
from honeybee_energy.simulation.daylightsaving import DaylightSavingTime
from honeybee_energy.simulation.output import SimulationOutput
from honeybee_energy.simulation.parameter import SimulationParameter
from honeybee_energy.simulation.runperiod import RunPeriod
from honeybee_energy.simulation.shadowcalculation import ShadowCalculation
from honeybee_energy.simulation.sizing import SizingParameter
from ladybug.dt import (
    Date,
    DateTime,
)
from pathlib import Path
from logging import getLogger

from ..config import (
    EFF_STANDARDS,
    SOLAR_DISTRIBUTIONS,
)


LOGGER = getLogger(__name__)

def load_measure(
    measure_path: Union[str, "PathLike[str]"],
    arguments: Optional["MeasureArgumentValues"] = None,
) -> Measure:
    """Load an OpenStudio measure folder and set measure arguments.

    Args:
        measure_path: OpenStudio measure folder containing ``measure.rb`` and
            ``measure.xml``.
        arguments: Measure argument values keyed by argument identifier.

    Returns:
        A validated Honeybee Energy measure object.
    """
    measure_dir = Path(measure_path)
    if not measure_dir.is_dir():
        raise NotADirectoryError(
            f"Measure folder does not exist: {measure_dir}"
        )

    measure_rb = measure_dir / "measure.rb"
    measure_xml = measure_dir / "measure.xml"

    if not measure_rb.is_file():
        raise FileNotFoundError(
            f"OpenStudio measure.rb was not found: {measure_rb}"
        )

    if not measure_xml.is_file():
        raise FileNotFoundError(
            f"OpenStudio measure.xml was not found: {measure_xml}"
        )

    measure = Measure(str(measure_dir))

    if arguments is not None:
        for arg in measure.arguments:
            arg = cast("MeasureArgument", arg)
            if arg.identifier not in arguments:
                continue

            value = arguments[arg.identifier]

            if value is None:
                continue

            if (
                arg.valid_choices == (None,)
                and str(value) == "None"
            ):
                continue

            arg.value = False if value is False else str(value)

    measure.validate()

    return measure

def simulation_output(
    zone_energy_use: bool = False,
    system_energy_use: bool = False,
    gains_and_losses: bool = False,
    comfort_metrics: bool = False,
    surface_temperature: bool = False,
    surface_energy_flow: bool = False,
    load_type: "LoadType" = "All",
    report_frequency: "ReportFrequency" = "Hourly",
) -> SimulationOutput:
    """Create an EnergyPlus output request for common simulation results.

    Args:
        zone_energy_use: Request zone-level energy use outputs.
        system_energy_use: Request HVAC and electricity generation outputs.
        gains_and_losses: Request thermal gain and loss outputs.
        comfort_metrics: Request comfort and unmet-hours outputs.
        surface_temperature: Request surface temperature outputs.
        surface_energy_flow: Request surface energy flow outputs.
        load_type: Energy load type used by zone and gains/losses requests.
        report_frequency: EnergyPlus reporting frequency.

    Returns:
        A Honeybee Energy simulation output object.
    """

    sim_output = SimulationOutput(
        reporting_frequency=report_frequency
    )

    if zone_energy_use:
        sim_output.add_zone_energy_use(load_type)

    if system_energy_use:
        sim_output.add_hvac_energy_use()
        sim_output.add_electricity_generation()

    if gains_and_losses:
        gains_load_type = "Total" if load_type == "All" else load_type
        sim_output.add_gains_and_losses(gains_load_type)

    if comfort_metrics:
        sim_output.add_comfort_metrics()
        sim_output.add_unmet_hours()

    if surface_temperature:
        sim_output.add_surface_temperature()

    if surface_energy_flow:
        sim_output.add_surface_energy_flow()

    return sim_output


def custom_simulation_output(
    output_names: Sequence[str],
    base_sim_output: Optional[SimulationOutput] = None,
    report_frequency: Optional["ReportFrequency"] = None,
    summary_reports: Optional[Sequence[str]] = None,
    unmet_setpt_tol: Optional[float] = None,
) -> SimulationOutput:
    """Create an EnergyPlus output request from explicit output names.

    Args:
        output_names: EnergyPlus output variable names.
        base_sim_output: Existing output request to duplicate before editing.
        report_frequency: EnergyPlus reporting frequency.
        summary_reports: EnergyPlus summary report names.
        unmet_setpt_tol: Unmet setpoint tolerance.

    Returns:
        A Honeybee Energy simulation output object.
    """
    sim_output = (
        base_sim_output.duplicate()
        if base_sim_output is not None
        else SimulationOutput()
    )

    if report_frequency is not None:
        sim_output.reporting_frequency = report_frequency.title()

    if output_names is not None:
        for o_n in output_names:
            sim_output.add_output(o_n)

    if summary_reports is not None:
        for report in summary_reports:
            sim_output.add_summary_report(report)

    if unmet_setpt_tol is not None:
        sim_output.unmet_setpoint_tolerance = unmet_setpt_tol

    return sim_output


def simulation_control(
    do_zone_sizing: bool = True,
    do_system_sizing: bool = True,
    do_plant_sizing: bool = True,
    for_sizing_period: bool = False,
    for_run_period: bool = True,
) -> SimulationControl:
    """Create simulation control flags for sizing and run periods.

    Args:
        do_zone_sizing: Run zone sizing calculations.
        do_system_sizing: Run system sizing calculations.
        do_plant_sizing: Run plant sizing calculations.
        for_sizing_period: Run the sizing periods.
        for_run_period: Run the weather file run period.

    Returns:
        A Honeybee Energy simulation control object.
    """
    return SimulationControl(
        do_zone_sizing,
        do_system_sizing,
        do_plant_sizing,
        for_sizing_period,
        for_run_period,
    )


def shadow_calculation(
    solar_dist: Optional["SolarDistributionKeys"] = None,
    calc_method: Optional["CalculationMethod"] = None,
    update_method: Optional["UpdateMethod"] = None,
    frequency: Optional[int] = None,
    max_figures: Optional[int] = None,
) -> ShadowCalculation:
    """Create EnergyPlus shadow calculation settings.

    Args:
        solar_dist: Solar distribution key or EnergyPlus value.
        calc_method: Shadow calculation method.
        update_method: Shadow calculation update method.
        frequency: Shadow calculation update frequency.
        max_figures: Maximum shadow figures.

    Returns:
        A Honeybee Energy shadow calculation object.
    """

    solar_dist = "FullExteriorWithReflections" if solar_dist is None else solar_dist
    try:
        solar_dist = SOLAR_DISTRIBUTIONS[solar_dist]
    except KeyError as e:
        raise ValueError(
            f"Invalid solar distribution key: {solar_dist}. "
            f"Valid keys are: {", ".join(SOLAR_DISTRIBUTIONS.keys())}"
        ) from e

    calc_method = "PolygonClipping" if calc_method is None else calc_method
    update_method = "Periodic" if update_method is None else update_method
    frequency = 30 if frequency is None else frequency
    max_figures = 15000 if max_figures is None else max_figures

    return ShadowCalculation(
        solar_dist,
        calc_method,
        update_method,
        frequency,
        max_figures,
    )


def sizing_parameter(
    ddy_file: Optional["PathLike[str]"] = None,
    filter_ddays: Optional[Literal[False, 0, 1, 2]] = None,
    heating_fac: Optional[float] = None,
    cooling_fac: Optional[float] = None,
    eff_standard: Optional["EfficiencyStandardKeys"] = None,
    climate_zone: Optional[str] = None,
    bldg_type: Optional[str] = None,
) -> SizingParameter:
    """Create sizing parameters for EnergyPlus translation.

    Args:
        ddy_file: Optional DDY file used to load design days.
        filter_ddays: Design day filter mode.
        heating_fac: Heating sizing factor.
        cooling_fac: Cooling sizing factor.
        eff_standard: ASHRAE or DOE efficiency standard key.
        climate_zone: ASHRAE climate zone.
        bldg_type: Building type used with efficiency standards.

    Returns:
        A Honeybee Energy sizing parameter object.
    """
    if eff_standard is not None and (
        heating_fac is not None or cooling_fac is not None
    ):
        LOGGER.warning(
            "Applying an ASHRAE efficiency standard requires the use of "
            "a heating factor of 1.25 and a cooling factor of 1.15. "
            "The input heating_fac and cooling_fac may be ignored during "
            "OpenStudio translation.",
        )

    heating_fac = 1.25 if heating_fac is None else heating_fac
    cooling_fac = 1.15 if cooling_fac is None else cooling_fac

    sizing = SizingParameter(
        None,
        heating_fac,
        cooling_fac,
    )

    if ddy_file is not None:
        if filter_ddays == 1:
            sizing.add_from_ddy_996_004(ddy_file)
        elif filter_ddays == 2:
            sizing.add_from_ddy_990_010(ddy_file)
        else:
            sizing.add_from_ddy(ddy_file)

    if eff_standard is not None:
        sizing.efficiency_standard = EFF_STANDARDS[eff_standard]
    if climate_zone is not None:
        sizing.climate_zone = climate_zone
    if bldg_type is not None:
        sizing.building_type = bldg_type

    return sizing


def simulation_parameter(
    north: Optional[float] = None,
    output: Optional[SimulationOutput] = None,
    run_period: Optional["AnalysisPeriod"]= None,
    daylight_saving: Optional["AnalysisPeriod"] = None,
    holidays: Optional[Sequence[str]] = None,
    start_dow: Optional[str] = None,
    timestep: Optional[int] = None,
    terrain: Optional["TerrainValues"] = None,
    simulation_control: Optional["SimulationControl"] = None,
    shadow_calculation: Optional["ShadowCalculation"] = None,
    sizing_parameter: Optional["SizingParameter"] = None,
) -> SimulationParameter:
    """Create the full Honeybee Energy simulation parameter object.

    Args:
        north: North angle in degrees.
        output: Simulation output request.
        run_period: Analysis period for the simulation.
        daylight_saving: Daylight saving analysis period.
        holidays: Holiday date strings.
        start_dow: Start day of week.
        timestep: Number of timesteps per hour.
        terrain: EnergyPlus terrain type.
        simulation_control: Simulation control settings.
        shadow_calculation: Shadow calculation settings.
        sizing_parameter: Sizing parameter settings.

    Returns:
        A Honeybee Energy simulation parameter object.
    """
    north_value = 0.0 if north is None else north

    if output is None:
        output = SimulationOutput()
        output.add_zone_energy_use()
        output.add_hvac_energy_use()

    if run_period is None:
        run_period_obj = RunPeriod()
    else:
        run_period_obj = RunPeriod.from_analysis_period(run_period)


    if daylight_saving is not None:
        run_period_obj.daylight_saving_time = (
            DaylightSavingTime.from_analysis_period(
                daylight_saving
            )
        )

    if holidays is not None and len(holidays) != 0:
        try:
            dates = tuple(
                Date.from_date_string(date)
                for date in holidays
            )
        except ValueError:
            dates = tuple(
                DateTime.from_date_time_string(date).date
                for date in holidays
            )
        run_period_obj.holidays = dates

    if start_dow is not None:
        run_period_obj.start_day_of_week = start_dow.title()

    timestep_value = 6 if timestep is None else timestep
    terrain_value = "City" if terrain is None else terrain.title()

    sim_par = SimulationParameter(
        output=output,
        run_period=run_period_obj,
        timestep=timestep_value,
        simulation_control=simulation_control,
        shadow_calculation=shadow_calculation,
        sizing_parameter=sizing_parameter,
        north_angle=north_value,  # pyright: ignore[reportArgumentType]
        terrain_type=terrain_value,
    )

    sim_par.north_angle = north_value

    return sim_par
