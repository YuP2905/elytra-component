from __future__ import annotations

from os import PathLike
from pathlib import Path
from typing import (
    Dict,
    Union,
    TYPE_CHECKING,
)

if TYPE_CHECKING:
    import numpy as np
    from numpy.typing import NDArray

    from ..typing import PitResult

from .common import (
    grid_count,
    grid_identifier,
    grid_infos,
    load_grid_res,
)


def read_pit_folder(
    result_folder: Union[str, PathLike[str]],
) -> Dict[str, "NDArray[np.float32]"]:
    """Read one point-in-time result folder.

    Args:
        result_folder: Folder containing point-in-time ``.res`` files and
            ``grids_info.json``.

    Returns:
        Sensor grid identifiers mapped to point-in-time result arrays.
    """
    folder = Path(result_folder)
    if not folder.is_dir():
        raise ValueError(
            f"Invalid point-in-time result folder: {folder}"
        )

    results: Dict[str, "NDArray[np.float32]"] = {}
    for grid_info in grid_infos(folder):
        grid_id = grid_identifier(grid_info)
        res_file = folder / f"{grid_id}.res"
        if not res_file.is_file():
            raise FileNotFoundError(
                f"Missing point-in-time result file: {res_file}"
            )

        results[grid_id] = load_grid_res(
            res_file,
            grid_count(grid_info),
            grid_info.get(
                "start_ln",
                0,
            ),
        )

    return results


def read_pit_results(
    result: "PitResult",
) -> Dict[str, "NDArray[np.float32]"]:
    """Read point-in-time simulation results keyed by sensor grid id.

    Args:
        result: Return value from ``run_pit_grid``.

    Returns:
        Sensor grid identifiers mapped to point-in-time result arrays.
    """
    values: Dict[str, "NDArray[np.float32]"] = {}
    for result_folder in result["results"]:
        for current_grid_id, array in read_pit_folder(result_folder).items():
            if current_grid_id in values:
                raise ValueError(
                    f"Duplicate point-in-time result grid id: {current_grid_id}"
                )
            values[current_grid_id] = array

    return values


def read_pit_grid(
    result: "PitResult",
    grid_id: str,
) -> "NDArray[np.float32]":
    """Read one point-in-time sensor grid result.

    Args:
        result: Return value from ``run_pit_grid``.
        grid_id: Sensor grid identifier.

    Returns:
        Point-in-time result values for the requested sensor grid.
    """
    values = read_pit_results(result)
    if grid_id not in values:
        raise KeyError(
            f"Point-in-time result grid was not found: {grid_id}"
        )
    return values[grid_id]
