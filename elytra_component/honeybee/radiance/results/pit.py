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
    read_res_folder,
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
    return read_res_folder(result_folder)


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
