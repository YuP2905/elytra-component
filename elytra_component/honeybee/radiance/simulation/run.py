from __future__ import annotations

from contextlib import contextmanager
import os
from os import PathLike
from pathlib import Path
from typing import (
    Dict,
    Iterator,
    Optional,
    List,
    Union,
    cast,
    TYPE_CHECKING,
)

if TYPE_CHECKING:
    from lbt_recipes.settings import RecipeSettings

    from ..typing import (
        AnnualGroupResult,
        AnnualResult,
        PitResult,
        PointInTimeMetric,
        SkyInput,
        SimulationScheduleInput,
    )

from lbt_recipes.recipe import Recipe

from ..config import (
    DEFAULT_ANNUAL_DAYLIGHT_RADIANCE_PARAMETERS,
    DEFAULT_ANNUAL_DAYLIGHT_THRESHOLDS,
    DEFAULT_POINT_IN_TIME_GRID_RADIANCE_PARAMETERS,
)


@contextmanager
def _suppress_stdout_stderr() -> Iterator[None]:
    """Suppress native stdout and stderr emitted by recipe runners.

    Args:
        None.

    Returns:
        Iterator context where file descriptors 1 and 2 point to ``os.devnull``.
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


def _recipe_output_path(
    recipe: Recipe,
    output_name: str,
    project_folder: Path,
) -> Path:
    """Return an output path from an lbt-recipes recipe run.

    Args:
        recipe: Completed lbt-recipes recipe.
        output_name: Recipe output name.
        project_folder: Recipe project folder.

    Returns:
        Output path resolved by the recipe.
    """
    return Path(
        cast(
            str,
            recipe.output_value_by_name(
                output_name,
                str(project_folder),
            )
        )
    )


def _npy_files(
    folder: Path,
) -> List[Path]:
    """Return sorted ``.npy`` files from a result folder.

    Args:
        folder: Result folder to search.

    Returns:
        Sorted ``.npy`` file paths.
    """
    return sorted(folder.glob("*.npy"))


def _res_files(
    folder: Path,
) -> Dict[str, Path]:
    """Return Radiance ``.res`` files keyed by file stem.

    Args:
        folder: Result folder to search.

    Returns:
        ``.res`` file paths keyed by file stem.
    """
    return {
        res_file.stem: res_file
        for res_file in sorted(folder.glob("*.res"))
    }


def _annual_groups(
    results_folder: Path,
) -> Dict[str, "AnnualGroupResult"]:
    """Find annual daylight aperture group result folders.

    Args:
        results_folder: Annual daylight recipe results folder.

    Returns:
        Aperture group metadata keyed by ``light_path/identifier``.
    """
    aperture_groups: Dict[str, "AnnualGroupResult"] = {}
    for total_dir in sorted(results_folder.glob("*/*/total")):
        if not total_dir.is_dir():
            continue

        group_folder = total_dir.parent
        direct_dir = group_folder / "direct"
        if not direct_dir.is_dir():
            continue

        light_path = group_folder.parent.name
        identifier = group_folder.name
        group_key = f"{light_path}/{identifier}"
        aperture_groups[group_key] = {
            "light_path": light_path,
            "identifier": identifier,
            "folder": group_folder,
            "total_dir": total_dir,
            "direct_dir": direct_dir,
            "total_npy": _npy_files(total_dir),
            "direct_npy": _npy_files(direct_dir),
        }

    if len(aperture_groups) == 0:
        raise RuntimeError(
            f"No annual daylight aperture group results were found in {results_folder}."
        )

    return aperture_groups


def run_annual(
    hbjson_file: Union[str, "PathLike[str]"],
    wea_file: Union[str, "PathLike[str]"],
    settings: Optional["RecipeSettings"] = None,
    north: float = 0.0,
    thresholds: str = DEFAULT_ANNUAL_DAYLIGHT_THRESHOLDS,
    schedule: Optional["SimulationScheduleInput"] = None,
    grid_filter: str = "*",
    radiance_parameters: str = DEFAULT_ANNUAL_DAYLIGHT_RADIANCE_PARAMETERS,
    enhanced: bool = True,
    *,
    radiance_check: bool = False,
    silent: bool = False,
) -> "AnnualResult":
    """Run annual daylight grid simulation from a Honeybee model and WEA.

    Args:
        hbjson_file: Honeybee model file.
        wea_file: Ladybug WEA file.
        settings: lbt-recipes run settings.
        north: North angle in degrees.
        thresholds: Annual daylight threshold string.
        schedule: Occupancy schedule input accepted by lbt-recipes.
        grid_filter: Sensor grid filter.
        radiance_parameters: Radiance command parameters.
        enhanced: Use the enhanced annual daylight recipe.
        radiance_check: Run Radiance dependency checks.
        silent: Suppress recipe process output.

    Returns:
        Paths and aperture group metadata for the recipe run.
    """
    hbjson_path = Path(hbjson_file)
    if not hbjson_path.is_file() or hbjson_path.suffix.lower() != ".hbjson":
        raise FileNotFoundError(
            f"HBJSON file '{hbjson_file}' does not exist or is not a valid HBJSON file."
        )
    wea_file = Path(wea_file)
    if not wea_file.is_file() or wea_file.suffix.lower() != ".wea":
        raise FileNotFoundError(
            f"WEA file '{wea_file}' does not exist or is not a valid WEA file."
        )

    recipe = Recipe(
        "annual-daylight-enhanced"
        if enhanced
        else "annual-daylight"
    )

    recipe.input_value_by_name(
        "model",
        str(hbjson_path),
    )
    recipe.input_value_by_name(
        "wea",
        str(wea_file),
    )

    recipe.input_value_by_name(
        "north",
        north,
    )
    recipe.input_value_by_name(
        "thresholds",
        thresholds,
    )
    if schedule is not None:
        recipe.input_value_by_name(
            "schedule",
            str(schedule)
            if isinstance(schedule, (str, PathLike))
            else schedule,
        )

    recipe.input_value_by_name(
        "grid-filter",
        grid_filter,
    )
    recipe.input_value_by_name(
        "radiance-parameters",
        radiance_parameters,
    )

    if silent:
        with _suppress_stdout_stderr():
            project_folder = Path(
                cast(
                    str,
                    recipe.run(
                        settings,
                        radiance_check=radiance_check,
                        silent=silent,
                    )
                )
            )
    else:
        project_folder = Path(
            cast(
                str,
                recipe.run(
                    settings,
                    radiance_check=radiance_check,
                    silent=silent,
                )
            )
        )

    simulation_id = recipe.simulation_id
    if simulation_id is None:
        raise RuntimeError(
            "Radiance recipe did not return a simulation id."
        )

    try:
        results_folder = _recipe_output_path(
            recipe,
            "results",
            project_folder,
        )
        metrics_folder = _recipe_output_path(
            recipe,
            "metrics",
            project_folder,
        )
        return {
            "project_folder": project_folder,
            "simulation_folder": project_folder / simulation_id,
            "results": results_folder,
            "metrics": metrics_folder,
            "aperture_groups": _annual_groups(results_folder),
        }
    except Exception as e:
        raise RuntimeError(
            recipe.failure_message(str(project_folder))
        ) from e


def run_pit_grid(
    hbjson_file: Union[str, "PathLike[str]"],
    sky: "SkyInput",
    settings: Optional["RecipeSettings"] = None,
    metric: "PointInTimeMetric" = "illuminance",
    grid_filter: str = "*",
    radiance_parameters: str = DEFAULT_POINT_IN_TIME_GRID_RADIANCE_PARAMETERS,
    *,
    radiance_check: bool = False,
    silent: bool = False,
) -> "PitResult":
    """Run point-in-time grid simulation from a Honeybee model and sky.

    Args:
        hbjson_file: Honeybee model file.
        sky: Honeybee Radiance sky input.
        settings: lbt-recipes run settings.
        metric: Point-in-time metric.
        grid_filter: Sensor grid filter.
        radiance_parameters: Radiance command parameters.
        radiance_check: Run Radiance dependency checks.
        silent: Suppress recipe process output.

    Returns:
        Paths and result file metadata for the recipe run.
    """
    hbjson_path = Path(hbjson_file)
    if not hbjson_path.is_file() or hbjson_path.suffix.lower() != ".hbjson":
        raise FileNotFoundError(
            f"HBJSON file '{hbjson_file}' does not exist or is not a valid HBJSON file."
        )

    recipe = Recipe("point-in-time-grid")
    recipe.input_value_by_name(
        "model",
        str(hbjson_path),
    )
    recipe.input_value_by_name(
        "sky",
        sky,
    )
    recipe.input_value_by_name(
        "metric",
        metric,
    )
    recipe.input_value_by_name(
        "grid-filter",
        grid_filter,
    )
    recipe.input_value_by_name(
        "radiance-parameters",
        radiance_parameters,
    )

    if silent:
        with _suppress_stdout_stderr():
            project_folder = Path(
                cast(
                    str,
                    recipe.run(
                        settings,
                        radiance_check=radiance_check,
                        silent=silent,
                    )
                )
            )
    else:
        project_folder = Path(
            cast(
                str,
                recipe.run(
                    settings,
                    radiance_check=radiance_check,
                    silent=silent,
                )
            )
        )

    simulation_id = recipe.simulation_id
    if simulation_id is None:
        raise RuntimeError(
            "Radiance recipe did not return a simulation id."
        )

    try:
        results_folders = [
            project_folder / simulation_id / "results" / "pit"
        ]
        grids_info = [
            results_folder / "grids_info.json"
            for results_folder in results_folders
        ]
        result_files: Dict[str, Path] = {}
        for results_folder in results_folders:
            results_folder = cast(Path, results_folder)
            result_files.update(_res_files(results_folder))

        if len(result_files) == 0:
            raise RuntimeError(
                "No point-in-time result files were found."
            )

        return {
            "project_folder": project_folder,
            "simulation_folder": project_folder / simulation_id,
            "results": results_folders,
            "grids_info": grids_info,
            "result_files": result_files,
        }
    except Exception as e:
        raise RuntimeError(
            recipe.failure_message(str(project_folder))
        ) from e
