from __future__ import annotations

from os import PathLike
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    cast,
)

from honeybee_energy.lib.schedules import schedule_by_identifier
from honeybee_energy.schedule.fixedinterval import ScheduleFixedInterval
from honeybee_energy.schedule.ruleset import ScheduleRuleset
from ladybug.datacollection import HourlyContinuousCollection
import numpy as np

if TYPE_CHECKING:
    from numpy.typing import NDArray

    from .typing import ScheduleInput


def schedule_array(
    schedule: "ScheduleInput",
) -> "NDArray[np.float32]":
    """Convert a Radiance schedule input to a 8760-value numeric array.

    Args:
        schedule: Schedule identifier, CSV path, Honeybee schedule, Ladybug
            hourly collection, or numeric sequence.

    Returns:
        Float32 schedule array with 8760 values.
    """
    if isinstance(schedule, str):
        schedule_path = Path(schedule)
        if schedule_path.is_file():
            values = np.genfromtxt(
                schedule_path,
                delimiter=",",
                dtype=np.float32,
            )
        else:
            honeybee_schedule = schedule_by_identifier(schedule)
            if honeybee_schedule is None:
                raise ValueError(
                    f"Schedule identifier was not found: {schedule}"
                )
            values = (
                honeybee_schedule.values()
                if isinstance(honeybee_schedule, ScheduleRuleset)
                else honeybee_schedule.values
            )
    elif isinstance(schedule, PathLike):
        values = np.genfromtxt(
            Path(schedule),
            delimiter=",",
            dtype=np.float32,
        )
    elif isinstance(schedule, ScheduleRuleset):
        values = schedule.values()
    elif isinstance(schedule, ScheduleFixedInterval):
        values = schedule.values
    elif isinstance(schedule, HourlyContinuousCollection):
        values = np.asarray(
            schedule.values,
            dtype=np.float32,
        )
    else:
        values = np.asarray(
            schedule,
            dtype=np.float32,
        )

    values = np.ravel(cast("NDArray[np.float32]", values))
    values = values[~np.isnan(values)]
    if values.shape[0] != 8760:
        raise ValueError(
            f"Schedule must contain 8760 numeric values. Got {values.shape[0]}."
        )
    return cast(
        "NDArray[np.float32]",
        values,
    )


def sun_up_mask(
    schedule_values: "NDArray[np.float32]",
    sun_up_hours: "NDArray[np.int64]",
) -> "NDArray[np.bool_]":
    """Return occupied sun-up columns for an annual daylight result matrix.

    Args:
        schedule_values: Schedule values for all 8760 hours.
        sun_up_hours: Sun-up hour indices represented by result columns.

    Returns:
        Boolean mask aligned to annual daylight matrix columns.
    """
    if schedule_values.shape[0] != 8760:
        raise ValueError(
            f"Schedule must contain 8760 values. Got {schedule_values.shape[0]}."
        )
    return cast(
        "NDArray[np.bool_]",
        schedule_values[sun_up_hours] >= 0.1,
    )


def sun_down_hours(
    schedule_values: "NDArray[np.float32]",
    sun_up_hours: "NDArray[np.int64]",
) -> int:
    """Return occupied hours not represented in sun-up result matrices.

    Args:
        schedule_values: Schedule values for all 8760 hours.
        sun_up_hours: Sun-up hour indices represented by result columns.

    Returns:
        Number of occupied hours outside the sun-up hours.
    """
    total_occupied = int(np.count_nonzero(schedule_values >= 0.1))
    sun_up_occupied = int(
        np.count_nonzero(
            sun_up_mask(
                schedule_values,
                sun_up_hours,
            )
        )
    )
    return total_occupied - sun_up_occupied


def filter_schedule(
    daylight_ill: "NDArray[np.float32]",
    occupied_sun_up_mask: "NDArray[np.bool_]",
) -> "NDArray[np.float32]":
    """Filter an annual daylight matrix to occupied sun-up columns.

    Args:
        daylight_ill: Illuminance matrix ordered as sensors by sun-up hours.
        occupied_sun_up_mask: Boolean mask aligned to matrix columns.

    Returns:
        Illuminance matrix containing only occupied sun-up columns.
    """
    if daylight_ill.ndim != 2:
        raise ValueError(
            f"Illuminance matrix must be 2D. Got {daylight_ill.shape}."
        )
    if daylight_ill.shape[1] != occupied_sun_up_mask.shape[0]:
        raise ValueError(
            "Illuminance column count must match sun-up schedule mask length. "
            f"Got {daylight_ill.shape[1]} and {occupied_sun_up_mask.shape[0]}."
        )
    return cast(
        "NDArray[np.float32]",
        daylight_ill[:, occupied_sun_up_mask],
    )
