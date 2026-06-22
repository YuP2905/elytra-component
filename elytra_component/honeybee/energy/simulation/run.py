from __future__ import annotations
from typing import (
    List,
    Tuple,
    Dict,
    Union,
    Optional,
    Iterator,
    Sequence,
    cast,
    TYPE_CHECKING,
)
if TYPE_CHECKING:
    from honeybee_energy.measure import Measure
    from os import PathLike
    from ..typing import (
        SimulationFiles,
        EnergySimulationResult,
        RunIDFResult,
        RunOSWResult,
        RunOSMResult,
    )

from honeybee.model import Model
from honeybee_energy.result.err import Err
from honeybee_energy.run import (
    to_openstudio_sim_folder,
    output_energyplus_files,
    run_idf,
    run_osw,
)
from honeybee_energy.result.osw import OSW
from honeybee_energy.simulation.parameter import SimulationParameter
from ladybug.epw import EPW
from ladybug.stat import STAT
from pathlib import Path
from contextlib import contextmanager

from honeybee.config import folders as hb_folders

import os
import json
import shutil
from logging import getLogger

LOGGER = getLogger(__name__)
@contextmanager
def _suppress_stdout_stderr() -> Iterator[None]:
    """Temporarily suppress stdout and stderr from external engines.

    Args:
        None.

    Returns:
        Iterator context that redirects stdout and stderr to ``os.devnull``.
    """
    stdout_fd = os.dup(1)
    stderr_fd = os.dup(2)

    with open(os.devnull, "w") as devnull:
        try:
            os.dup2(devnull.fileno(), 1)
            os.dup2(devnull.fileno(), 2)
            yield
        finally:
            os.dup2(stdout_fd, 1)
            os.dup2(stderr_fd, 2)
            os.close(stdout_fd)
            os.close(stderr_fd)

def _check_sim_err(
    err_file: Optional[Union[str, "PathLike[str]"]]
) -> Optional[str]:
    """Read an EnergyPlus ERR file and raise on fatal errors.

    Args:
        err_file: Optional EnergyPlus ERR file path.

    Returns:
        ERR file contents when an ERR file exists, otherwise ``None``.
    """
    if err_file is None:
        return None

    err_path = Path(err_file)
    if not err_path.is_file():
        return None

    err = Err(str(err_path))
    severe_errors = cast(
        List[str],
        err.severe_errors
    )
    for severe_err in severe_errors:
        LOGGER.warning(severe_err)

    fatal_errors = cast(
        List[str],
        err.fatal_errors
    )
    if len(fatal_errors) > 0:
        LOGGER.warning(err.file_contents)
        raise RuntimeError(
            "\n".join(fatal_errors)
        )

    return err.file_contents

def write_hbjson_2_osm(
    hbjson_file: Union[str, "PathLike[str]"],
    epw_file: Union[str, "PathLike[str]"],
    folder: Optional[Union[str, "PathLike[str]"]] = None,
    sim_par: Optional[SimulationParameter] = None,
    measures: Optional[List["Measure"]] = None,
    add_str: Optional[Sequence[str]] = None,
    *,
    write_sim_param_json: bool = False,
) -> "SimulationFiles":
    """Write a Honeybee model and simulation inputs to an OpenStudio folder.

    Args:
        hbjson_file: Honeybee model file.
        epw_file: EPW weather file.
        folder: Optional output folder.
        sim_par: Optional Honeybee Energy simulation parameter object.
        measures: Optional OpenStudio measures.
        add_str: Optional IDF strings injected during translation.
        write_sim_param_json: Whether to write ``simulation_parameters.json``.

    Returns:
        Generated OSM, OSW, IDF, and optional simulation parameter file paths.
    """
    hbjson_path = Path(hbjson_file)
    if not hbjson_path.is_file() or hbjson_path.suffix.lower() != ".hbjson":
        raise FileNotFoundError(
            f"HBJSON file '{hbjson_file}' does not exist or is not a valid HBJSON file."
        )
    hb_model = cast(Model, Model.from_hbjson(
        str(hbjson_path),
        cleanup_irrational=True,
    ))

    epw_path = Path(epw_file)
    if not epw_path.is_file() or epw_path.suffix.lower() != ".epw":
        raise FileNotFoundError(
            f"EPW file '{epw_file}' does not exist or is not a valid EPW file."
        )


    if sim_par is None:
        sim_par = SimulationParameter()
        sim_par.output.add_zone_energy_use()
        sim_par.output.add_hvac_energy_use()
        sim_par.output.add_electricity_generation()
    else:
        sim_par = sim_par.duplicate()


    if len(sim_par.sizing_parameter.design_days) == 0:
        ddy_path = epw_path.with_suffix(".ddy")
        ddy_error: Optional[Exception] = None

        if ddy_path.is_file():
            try:
                sim_par.sizing_parameter.add_from_ddy_996_004(
                    str(ddy_path)
                )
            except (AssertionError, ValueError) as error:
                ddy_error = error

        if len(sim_par.sizing_parameter.design_days) == 0:
            if ddy_path.is_file() and ddy_error is not None:
                warning_msg = (
                    "\nNo ddy_file was input into the sim_par sizing parameters "
                    "and the .ddy file next to the epw_file could not be parsed."
                )
            elif ddy_path.is_file():
                warning_msg = (
                    "\nNo ddy_file was input into the sim_par sizing parameters "
                    "and no design days were found in the .ddy file next to "
                    "the epw_file."
                )
            else:
                warning_msg = (
                    "\nNo ddy_file was input into the sim_par sizing parameters "
                    "and no .ddy file was found next to the epw_file."
                )

            epw = EPW(
                str(epw_path)
            )
            sim_par.sizing_parameter.design_days = [
                epw.approximate_design_day("WinterDesignDay"),
                epw.approximate_design_day("SummerDesignDay"),
            ]
            LOGGER.warning(
                warning_msg
                + " Design days were generated from the input epw_file, "
                +"but this is less accurate than design days from DDY files.",
                stacklevel=2
            )

    if sim_par.sizing_parameter.climate_zone is None:
        stat_path = epw_path.with_suffix(".stat")
        if stat_path.is_file():
            stat = STAT(str(stat_path))
            sim_par.sizing_parameter.climate_zone = stat.ashrae_climate_zone

    output_dir = Path(folder) if folder is not None \
        else Path(cast(str, hb_folders.default_simulation_folder))
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if write_sim_param_json:
        sim_par_json = output_dir / "simulation_parameters.json"
        sim_par_json.write_text(
            json.dumps(
                sim_par.to_dict(),
                ensure_ascii=False,
                indent=4,
            ),
            encoding="utf-8"
        )
    else:
        sim_par_json = None

    schedule_dir = output_dir / "schedules"
    schedule_dir.mkdir()

    add_idf_str = (
        "\n".join(add_str)
        if add_str is not None and len(add_str) != 0 and add_str[0] is not None
        else None
    )


    osm_file, osw_file, idf_file = cast(
        Tuple[str, str, str],
        to_openstudio_sim_folder(
            model = hb_model,
            directory = str(folder),
            epw_file = str(epw_path),
            sim_par = sim_par,
            schedule_directory = str(schedule_dir),
            enforce_rooms = True,
            additional_measures = measures,
            strings_to_inject = add_idf_str,
        )
    )

    osm_path = Path(osm_file)
    if not osm_path.is_file():
        raise RuntimeError(
            f"OpenStudio OSM file was not generated: {osm_path}"
        )

    osw_path = Path(osw_file) if osw_file is not None else None
    idf_path = Path(idf_file) if idf_file is not None else None

    return {
        "osm": osm_path,
        "osw": osw_path,
        "idf": idf_path,
        "sim_params": sim_par_json
    }

def run_energy_simulation(
    ops_files: "SimulationFiles",
    epw_file: Union[str, "PathLike[str]"],
    silent: bool = False,
) -> "EnergySimulationResult":
    """Run EnergyPlus from generated OpenStudio simulation files.

    Args:
        ops_files: Files generated by ``write_hbjson_2_osm``.
        epw_file: EPW weather file.
        silent: Whether to suppress external engine output.

    Returns:
        Generated OSM, IDF, SQL, ZSZ, RDD, HTML, and ERR result paths.
    """
    epw_path = Path(epw_file)
    if not epw_path.is_file() or epw_path.suffix.lower() != ".epw":
        raise FileNotFoundError(
            f"EPW file '{epw_file}' does not exist or is not a valid EPW file."
        )

    osm_path = ops_files.get("osm")
    osw_path = ops_files.get("osw")
    idf_path = ops_files.get("idf")

    if not osm_path.is_file():
        raise FileNotFoundError(
            f"OpenStudio OSM file '{osm_path}' does not exist."
        )

    if osw_path is not None and osw_path.is_file():
        if silent:
            with _suppress_stdout_stderr():
                osm_file, idf_file = run_osw(
                    str(osw_path),
                    measures_only=False,
                    silent=silent
                )
        else:
            osm_file, idf_file = run_osw(
                str(osw_path),
                measures_only=False,
                silent=silent
            )

        if idf_file is None:
            raise RuntimeError(
                f"OpenStudio simulation did not generate an IDF file: {osw_path}"
            )

        osm_path = Path(osm_file) if osm_file is not None else osm_path
        idf_path = Path(idf_file)

        sql, zsz, rdd, html, err = output_energyplus_files(
            str(idf_path.parent),
        )

    else:
        if idf_path is None or not idf_path.is_file():
            raise FileNotFoundError(
                f"OpenStudio IDF file '{idf_path}' does not exist."
                " Run write_hbjson_2_osm(...) first."
            )
        if silent:
            with _suppress_stdout_stderr():
                sql, zsz, rdd, html, err = run_idf(
                    str(idf_path),
                    str(epw_path),
                    silent=silent
                )
        else:
            sql, zsz, rdd, html, err = run_idf(
                str(idf_path),
                str(epw_path),
                silent=silent
            )

    err = Path(err) if err is not None else None
    _check_sim_err(err)

    if sql is None:
        raise RuntimeError(
            f"EnergyPlus simulation did not generate an SQL file: {idf_path}"
        )

    sql = Path(sql)
    zsz = Path(zsz) if zsz is not None else None
    rdd = Path(rdd) if rdd is not None else None
    html = Path(html) if html is not None else None

    return {
        "osm": osm_path,
        "idf": idf_path,
        "sql": sql,
        "zsz": zsz,
        "rdd": rdd,
        "html": html,
        "err": err,
    }

def run_idf_simulation(
    idf_path: Path,
    epw_path: Path,
    add_str: Optional[Sequence[Optional[str]]] = None,
    silent: bool = False,
) -> "RunIDFResult":
    """Run an EnergyPlus IDF file.

    Args:
        idf_path: IDF file path.
        epw_path: EPW weather file path.
        add_str: Optional IDF strings appended before simulation.
        silent: Whether to suppress external engine output.

    Returns:
        Generated SQL, ZSZ, RDD, and HTML result paths.
    """
    add_idf_str = (
        "\n".join(text for text in add_str if text is not None)
        if add_str is not None and len(add_str) != 0 and add_str[0] is not None
        else None
    )

    if add_idf_str is not None:
        with idf_path.open("a", encoding="utf-8") as idf_file:
            idf_file.write("\n")
            idf_file.write(add_idf_str)


    if silent:
        with _suppress_stdout_stderr():
            sql, zsz, rdd, html, err = run_idf(
                str(idf_path),
                str(epw_path),
                silent=silent,
            )
    else:
        sql, zsz, rdd, html, err = run_idf(
            str(idf_path),
            str(epw_path),
            silent=silent,
        )

    err = Path(err) if err is not None else None
    _check_sim_err(err)
    if sql is None:
        raise RuntimeError(
            f"EnergyPlus simulation did not generate an SQL file: {idf_path}"
        )

    sql = Path(sql)
    zsz = Path(zsz) if zsz is not None else None
    rdd = Path(rdd) if rdd is not None else None
    html = Path(html) if html is not None else None

    return {
        "sql": sql,
        "zsz": zsz,
        "rdd":  rdd,
        "html": html,
    }


def run_osw_simulation(
    osw_file: Union[str, "PathLike[str]"],
    epw_file: Union[str, "PathLike[str]"],
    add_str: Optional[Sequence[Optional[str]]] = None,
    silent: bool = False,
) -> "RunOSWResult":
    """Run an OpenStudio workflow and the generated IDF.

    Args:
        osw_file: OpenStudio workflow file.
        epw_file: EPW weather file.
        add_str: Optional IDF strings appended before EnergyPlus simulation.
        silent: Whether to suppress external engine output.

    Returns:
        Generated OSM, IDF, SQL, ZSZ, RDD, and HTML result paths.
    """
    osw_path = Path(osw_file)
    if not osw_path.is_file() or osw_path.suffix.lower() != ".osw":
        raise FileNotFoundError(
            f"OpenStudio OSW file '{osw_file}' does not exist or is not a valid OSW file."
        )

    epw_path = Path(epw_file)
    if not epw_path.is_file() or epw_path.suffix.lower() != ".epw":
        raise FileNotFoundError(
            f"EPW file '{epw_file}' does not exist or is not a valid EPW file."
        )

    if silent:
        with _suppress_stdout_stderr():
            osm, idf = run_osw(
                str(osw_path),
                silent=silent,
            )
    else:
        osm, idf = run_osw(
            str(osw_path),
            silent=silent,
        )

    osm_path = Path(osm) if osm is not None else None
    idf_path = Path(idf) if idf is not None else None

    if osm_path is None or not osm_path.is_file():
        raise RuntimeError(
            f"OpenStudio workflow did not generate an OSM file: {osw_path}"
        )

    if idf_path is None or not idf_path.is_file():
        raise RuntimeError(
            f"OpenStudio workflow did not generate an IDF file: {osw_path}"
        )

    add_idf_str = (
        "\n".join(text for text in add_str if text is not None)
        if add_str is not None and len(add_str) != 0 and add_str[0] is not None
        else None
    )

    if add_idf_str is not None:
        with idf_path.open("a", encoding="utf-8") as idf_file:
            idf_file.write("\n")
            idf_file.write(add_idf_str)

    if silent:
        with _suppress_stdout_stderr():
            sql, zsz, rdd, html, err = run_idf(
                str(idf_path),
                str(epw_path),
                silent=silent,
            )
    else:
        sql, zsz, rdd, html, err = run_idf(
            str(idf_path),
            str(epw_path),
            silent=silent,
        )

    _check_sim_err(err)

    if sql is None:
        raise RuntimeError(
            f"EnergyPlus simulation did not generate an SQL file: {idf_path}"
        )

    return {
        "osm": osm_path,
        "idf": idf_path,
        "sql": Path(sql),
        "zsz": Path(zsz) if zsz is not None else None,
        "rdd": Path(rdd) if rdd is not None else None,
        "html": Path(html) if html is not None else None,
    }


def run_osm_simulation(
    osm_file: Union[str, "PathLike[str]"],
    epw_file: Union[str, "PathLike[str]"],
    add_str: Optional[Sequence[Optional[str]]] = None,
    silent: bool = False,
) -> "RunOSMResult":
    """Run an OpenStudio model through an OSW file and EnergyPlus.

    Args:
        osm_file: OpenStudio model file.
        epw_file: EPW weather file.
        add_str: Optional IDF strings appended before EnergyPlus simulation.
        silent: Whether to suppress external engine output.

    Returns:
        Generated IDF, SQL, ZSZ, RDD, and HTML result paths.
    """
    osm_path = Path(osm_file)
    if not osm_path.is_file() or osm_path.suffix.lower() != ".osm":
        raise FileNotFoundError(
            f"OSM file does not exist or is not an OSM file: {osm_path}"
        )

    epw_path = Path(epw_file)
    if not epw_path.is_file() or epw_path.suffix.lower() != ".epw":
        raise FileNotFoundError(
            f"EPW file does not exist or is not an EPW file: {epw_path}"
        )

    osw_dir = osm_path.parent
    osw_path = osw_dir / "workflow.osw"

    osw_data: Dict[str, Union[str, List[str]]] = {
        "seed_file": str(osm_path),
        "weather_file": str(epw_path),
    }

    schedule_dir_1 = osw_dir.parent / "schedules"
    schedule_dir_2 = osw_dir / "schedules"

    if schedule_dir_1.is_dir():
        osw_data["file_paths"] = [str(schedule_dir_1)]
    elif schedule_dir_2.is_dir():
        osw_data["file_paths"] = [str(schedule_dir_2)]

    osw_path.write_text(
        json.dumps(
            osw_data,
            indent=4,
        ),
        encoding="utf-8",
    )

    if silent:
        with _suppress_stdout_stderr():
            _, idf_file = run_osw(
                str(osw_path),
                silent=silent,
            )
    else:
        _, idf_file = run_osw(
            str(osw_path),
            silent=silent,
        )

    if idf_file is None:
        out_osw_path = osw_dir / "out.osw"

        if out_osw_path.is_file():
            log_osw = OSW(str(out_osw_path))
            errors: List[str] = []

            osw_errors = cast(
                List[str],
                log_osw.errors
            )
            osw_error_tracebacks = cast(
                List[str],
                log_osw.error_tracebacks
            )
            for error, traceback in zip(
                osw_errors,
                osw_error_tracebacks,
            ):
                LOGGER.error(traceback)
                errors.append(error)

            raise RuntimeError(
                "Failed to run OpenStudio CLI:\n"
                + "\n".join(errors)
            )

        raise RuntimeError(
            f"OpenStudio CLI did not generate an IDF file: {osw_path}"
        )

    idf_path = Path(idf_file)
    if not idf_path.is_file():
        raise RuntimeError(
            f"IDF file was not generated: {idf_path}"
        )

    add_idf_str = (
        "\n".join(text for text in add_str if text is not None)
        if add_str is not None and len(add_str) != 0 and add_str[0] is not None
        else None
    )

    if add_idf_str is not None:
        with idf_path.open("a", encoding="utf-8") as idf:
            idf.write("\n")
            idf.write(add_idf_str)

    if silent:
        with _suppress_stdout_stderr():
            sql, zsz, rdd, html, err = run_idf(
                str(idf_path),
                str(epw_path),
                silent=silent,
            )
    else:
        sql, zsz, rdd, html, err = run_idf(
            str(idf_path),
            str(epw_path),
            silent=silent,
        )

    _check_sim_err(err)

    if sql is None:
        raise RuntimeError(
            f"EnergyPlus simulation did not generate an SQL file: {idf_path}"
        )

    return {
        "idf": idf_path,
        "sql": Path(sql),
        "zsz": Path(zsz) if zsz is not None else None,
        "rdd": Path(rdd) if rdd is not None else None,
        "html": Path(html) if html is not None else None,
    }
