from __future__ import annotations
from os import PathLike
from pathlib import Path
from typing import (
    Dict,
    Union,
    cast,
    TYPE_CHECKING,
)
if TYPE_CHECKING:
    from numpy.typing import NDArray
    from .typing import (
        RadianceOptionTuple,
        RadianceOptionValues,
    )

import numpy as np

def option_values(
    option_map: Dict[str, "RadianceOptionTuple"],
    detail_level: int,
) -> "RadianceOptionValues":
    """Return Radiance option values for a detail level.

    Args:
        option_map: Option values grouped by Radiance option name.
        detail_level: Detail level index.

    Returns:
        Option names mapped to the selected values.
    """
    return {
        option_name: values[detail_level]
        for option_name, values in option_map.items()
    }

def load_npy(
    npy_file: Union[str, PathLike[str]],
) -> "NDArray[np.float32]":
    """Load one Radiance result matrix from a ``.npy`` file.

    Args:
        npy_file: Radiance annual result matrix file.

    Returns:
        Float32 matrix with shape ``(sensor_count, timestep_count)``.
    """
    npy_file = Path(npy_file)
    if not npy_file.is_file() or npy_file.suffix.lower() != ".npy":
        raise ValueError(
            f"Invalid annual illuminance npy file: {npy_file}"
        )
    array = cast(
        "NDArray[np.float32]",
        np.load(Path(npy_file))
    )
    if array.ndim != 2:
        raise ValueError(
            "Result npy must have shape "
            f"(sensor_count, timestep_count). Got {array.shape}."
        )
    return cast(
        "NDArray[np.float32]",
        np.asarray(
            array,
            dtype=np.float32,
        ),
    )


def load_sun_up_hours(
    sun_up_hours_file: Union[str, PathLike[str]],
) -> "NDArray[np.int64]":
    """Load sun-up HOY indices from annual daylight results.

    Args:
        sun_up_hours_file: Annual daylight ``sun-up-hours.txt`` file.

    Returns:
        Integer HOY indices represented by annual daylight result columns.
    """
    values = np.loadtxt(
        Path(sun_up_hours_file),
        dtype=np.float64,
    )
    if values.ndim != 1:
        raise ValueError(
            f"Sun-up hours must be a 1D vector. Got {values.shape}."
        )

    indices = np.floor(values).astype(np.int64)
    if np.any(indices < 0) or np.any(indices >= 8760):
        raise ValueError(
            "Sun-up hour indices must be between 0 and 8759."
        )
    return cast(
        "NDArray[np.int64]",
        indices,
    )
