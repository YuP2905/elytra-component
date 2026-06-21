from __future__ import annotations

import json
from os import PathLike
from pathlib import Path
from typing import (
    List,
    Union,
    cast,
    TYPE_CHECKING,
)

import numpy as np

if TYPE_CHECKING:
    from numpy.typing import NDArray

    from ..typing import SensorGridInfo


def check_sensor_count(
    array: "NDArray[np.float32]",
    sensor_count: int,
    source: Path,
) -> None:
    """Validate that a result array has the expected sensor count.

    Args:
        array: Result values loaded from a Radiance result file.
        sensor_count: Expected number of sensors.
        source: Source file used in the validation error.

    Returns:
        None.
    """
    if array.shape[0] != sensor_count:
        raise ValueError(
            f"Expected {sensor_count} sensor values in {source}. Got {array.shape[0]}."
        )


def load_res(
    res_file: Union[str, PathLike[str]],
) -> "NDArray[np.float32]":
    """Load one Radiance ``.res`` file as a one-dimensional float array.

    Args:
        res_file: Radiance result file.

    Returns:
        One-dimensional float32 result array.
    """
    res_path = Path(res_file)
    if not res_path.is_file() or res_path.suffix.lower() != ".res":
        raise ValueError(
            f"Invalid Radiance result file: {res_path}"
        )

    values = np.loadtxt(
        res_path,
        dtype=np.float32,
    )
    return cast(
        "NDArray[np.float32]",
        np.atleast_1d(values).astype(
            np.float32,
            copy=False,
        ),
    )


def grid_infos(
    result_folder: Path,
) -> List["SensorGridInfo"]:
    """Read sensor grid metadata from a Radiance result folder.

    Args:
        result_folder: Folder containing ``grids_info.json``.

    Returns:
        Sensor grid metadata records.
    """
    grids_info_file = result_folder / "grids_info.json"
    if not grids_info_file.is_file():
        raise ValueError(
            f"Radiance result folder contains no grids_info.json: {result_folder}"
        )

    with grids_info_file.open(
        "r",
        encoding="utf-8",
    ) as json_file:
        grid_info_values = cast(
            List["SensorGridInfo"],
            json.load(json_file),
        )
    return grid_info_values


def grid_identifier(
    grid_info: "SensorGridInfo",
) -> str:
    """Return the sensor grid identifier used by result files.

    Args:
        grid_info: One sensor grid metadata record.

    Returns:
        ``full_id`` when available, otherwise ``identifier``.
    """
    if "full_id" in grid_info:
        return grid_info["full_id"]
    if "identifier" in grid_info:
        return grid_info["identifier"]
    raise KeyError(
        "Sensor grid info must include 'full_id' or 'identifier'."
    )


def grid_count(
    grid_info: "SensorGridInfo",
) -> int:
    """Return the sensor count for one sensor grid.

    Args:
        grid_info: One sensor grid metadata record.

    Returns:
        Number of sensors in the grid.
    """
    if "count" not in grid_info:
        raise KeyError(
            "Sensor grid info must include 'count'."
        )
    return grid_info["count"]


def load_grid_res(
    res_file: Path,
    sensor_count: int,
    start_line: int,
) -> "NDArray[np.float32]":
    """Load one sensor grid block from a Radiance ``.res`` file.

    Args:
        res_file: Radiance result file.
        sensor_count: Number of rows to load.
        start_line: First row for this grid in the result file.

    Returns:
        One-dimensional sensor result values.
    """
    values = np.loadtxt(
        res_file,
        dtype=np.float32,
        skiprows=start_line,
        max_rows=sensor_count,
    )
    array = cast(
        "NDArray[np.float32]",
        np.atleast_1d(values).astype(
            np.float32,
            copy=False,
        ),
    )
    if array.shape[0] != sensor_count:
        check_sensor_count(
            array,
            sensor_count,
            res_file,
        )
    return array
