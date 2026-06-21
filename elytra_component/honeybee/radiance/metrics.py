from __future__ import annotations

from contextlib import redirect_stderr
from io import StringIO
from typing import (
    Dict,
    Optional,
    TYPE_CHECKING,
    cast,
)

import numpy as np

from .typing import DaylightMetrics

with redirect_stderr(StringIO()):
    from honeybee_radiance_postprocess import IS_GPU as POSTPROCESS_IS_GPU
    from honeybee_radiance_postprocess import np as postprocess_np
    from honeybee_radiance_postprocess.metrics import (
        ase_array2d,
        cda_array2d,
        da_array2d,
        udi_array2d,
        udi_lower_array2d,
        udi_upper_array2d,
    )

if TYPE_CHECKING:
    from pathlib import Path
    from numpy.typing import NDArray

    from .typing import (
        AnnualGroupResult,
        AnnualResult,
        AnnualMetrics,
        GridMetrics,
        ScheduleInput,
    )


from .schedule import (
    schedule_array,
    filter_schedule,
    sun_down_hours,
    sun_up_mask,
)
from .utils import (
    load_npy,
    load_sun_up_hours,
)


def da_map(
    daylight_ill: "NDArray[np.float32]",
    threshold: float = 300.0,
    *,
    occupied_hours: Optional[int] = None,
) -> "NDArray[np.float32]":
    """Calculate daylight autonomy fraction for each sensor.

    Args:
        daylight_ill: Illuminance matrix ordered as sensors by timesteps.
        threshold: Illuminance threshold in lux.
        occupied_hours: Number of occupied hours used as denominator.

    Returns:
        DA fraction values for each sensor.
    """
    if occupied_hours is None:
        occupied_hours = daylight_ill.shape[1]
    if occupied_hours <= 0:
        raise ValueError("occupied_hours must be greater than 0.")

    result = da_array2d(
        cast("NDArray[np.float32]", postprocess_np.asarray(daylight_ill)),
        total_occ=occupied_hours,
        threshold=threshold,
    )
    if POSTPROCESS_IS_GPU:
        result = postprocess_np.asnumpy(cast("NDArray[np.float32]", result))

    return cast(
        "NDArray[np.float32]",
        np.asarray(
            result / 100.0,
            dtype=np.float32,
        ),
    )


def cda_map(
    daylight_ill: "NDArray[np.float32]",
    threshold: float = 300.0,
    *,
    occupied_hours: Optional[int] = None,
) -> "NDArray[np.float32]":
    """Calculate continuous daylight autonomy fraction for each sensor.

    Args:
        daylight_ill: Illuminance matrix ordered as sensors by timesteps.
        threshold: Illuminance threshold in lux.
        occupied_hours: Number of occupied hours used as denominator.

    Returns:
        Continuous DA fraction values for each sensor.
    """
    if occupied_hours is None:
        occupied_hours = daylight_ill.shape[1]
    if occupied_hours <= 0:
        raise ValueError("occupied_hours must be greater than 0.")

    result = cda_array2d(
        cast("NDArray[np.float32]", postprocess_np.asarray(daylight_ill)),
        total_occ=occupied_hours,
        threshold=threshold,
    )
    if POSTPROCESS_IS_GPU:
        result = postprocess_np.asnumpy(cast("NDArray[np.float32]", result))

    return cast(
        "NDArray[np.float32]",
        np.asarray(
            result / 100.0,
            dtype=np.float32,
        ),
    )


def udi_map(
    daylight_ill: "NDArray[np.float32]",
    lower_threshold: float = 100.0,
    upper_threshold: float = 3000.0,
    *,
    occupied_hours: Optional[int] = None,
) -> "NDArray[np.float32]":
    """Calculate useful daylight illuminance fraction for each sensor.

    Args:
        daylight_ill: Illuminance matrix ordered as sensors by timesteps.
        lower_threshold: Lower useful illuminance threshold in lux.
        upper_threshold: Upper useful illuminance threshold in lux.
        occupied_hours: Number of occupied hours used as denominator.

    Returns:
        UDI fraction values for each sensor.
    """
    if occupied_hours is None:
        occupied_hours = daylight_ill.shape[1]
    if occupied_hours <= 0:
        raise ValueError("occupied_hours must be greater than 0.")

    result = udi_array2d(
        cast("NDArray[np.float32]", postprocess_np.asarray(daylight_ill)),
        total_occ=occupied_hours,
        min_t=lower_threshold,
        max_t=upper_threshold,
    )
    if POSTPROCESS_IS_GPU:
        result = postprocess_np.asnumpy(cast("NDArray[np.float32]", result))

    return cast(
        "NDArray[np.float32]",
        np.asarray(
            result / 100.0,
            dtype=np.float32,
        ),
    )


def udi_low_map(
    daylight_ill: "NDArray[np.float32]",
    lower_threshold: float = 100.0,
    *,
    occupied_hours: Optional[int] = None,
    sun_down_hours: int = 0,
) -> "NDArray[np.float32]":
    """Calculate lower-than-UDI fraction for each sensor.

    Args:
        daylight_ill: Illuminance matrix ordered as sensors by timesteps.
        lower_threshold: Lower useful illuminance threshold in lux.
        occupied_hours: Number of occupied hours used as denominator.
        sun_down_hours: Occupied hours without sun-up result columns.

    Returns:
        Lower-than-UDI fraction values for each sensor.
    """
    if occupied_hours is None:
        occupied_hours = daylight_ill.shape[1] + sun_down_hours
    if occupied_hours <= 0:
        raise ValueError("occupied_hours must be greater than 0.")

    result = udi_lower_array2d(
        cast("NDArray[np.float32]", postprocess_np.asarray(daylight_ill)),
        total_occ=occupied_hours,
        min_t=lower_threshold,
        sun_down_occ_hours=sun_down_hours,
    )
    if POSTPROCESS_IS_GPU:
        result = postprocess_np.asnumpy(cast("NDArray[np.float32]", result))

    return cast(
        "NDArray[np.float32]",
        np.asarray(
            result / 100.0,
            dtype=np.float32,
        ),
    )


def udi_up_map(
    daylight_ill: "NDArray[np.float32]",
    upper_threshold: float = 3000.0,
    *,
    occupied_hours: Optional[int] = None,
) -> "NDArray[np.float32]":
    """Calculate higher-than-UDI fraction for each sensor.

    Args:
        daylight_ill: Illuminance matrix ordered as sensors by timesteps.
        upper_threshold: Upper useful illuminance threshold in lux.
        occupied_hours: Number of occupied hours used as denominator.

    Returns:
        Higher-than-UDI fraction values for each sensor.
    """
    if occupied_hours is None:
        occupied_hours = daylight_ill.shape[1]
    if occupied_hours <= 0:
        raise ValueError("occupied_hours must be greater than 0.")

    result = udi_upper_array2d(
        cast("NDArray[np.float32]", postprocess_np.asarray(daylight_ill)),
        total_occ=occupied_hours,
        max_t=upper_threshold,
    )
    if POSTPROCESS_IS_GPU:
        result = postprocess_np.asnumpy(cast("NDArray[np.float32]", result))

    return cast(
        "NDArray[np.float32]",
        np.asarray(
            result / 100.0,
            dtype=np.float32,
        ),
    )


def sda(
    DA_map: "NDArray[np.float32]",
    threshold: float = 0.5,
) -> float:
    """Calculate spatial daylight autonomy from a DA map.

    Args:
        DA_map: Daylight autonomy fraction values for each sensor.
        threshold: Minimum DA fraction for a passing sensor.

    Returns:
        Fraction of sensors passing the DA target.
    """
    return float(np.mean(DA_map >= threshold))


def ase_map(
    direct_ill: "NDArray[np.float32]",
    threshold: float = 1000.0,
) -> "NDArray[np.float32]":
    """Calculate annual sunlight exposure hours for each sensor.

    Args:
        direct_ill: Direct illuminance matrix ordered as sensors by timesteps.
        threshold: Direct illuminance threshold in lux.

    Returns:
        Direct-sun hours above threshold for each sensor.
    """
    _, result = ase_array2d(
        cast("NDArray[np.float32]", postprocess_np.asarray(direct_ill)),
        direct_threshold=threshold,
    )
    if POSTPROCESS_IS_GPU:
        result = postprocess_np.asnumpy(cast("NDArray[np.float32]", result))

    return cast(
        "NDArray[np.float32]",
        np.asarray(
            result,
            dtype=np.float32,
        ),
    )


def ase(
    ASE_map: "NDArray[np.float32]",
    threshold: float = 250.0,
) -> float:
    """Calculate annual sunlight exposure fraction.

    Args:
        ASE_map: Direct-sun hours for each sensor.
        threshold: Maximum acceptable direct-sun hours.

    Returns:
        Fraction of sensors above the direct-sun hour threshold.
    """
    return float(np.mean(ASE_map >= threshold))


def uniformity_map(
    daylight_ill: "NDArray[np.float32]",
) -> "NDArray[np.float32]":
    """Calculate min-to-mean illuminance ratio for each timestep.

    Args:
        daylight_ill: Illuminance matrix ordered as sensors by timesteps.

    Returns:
        Uniformity ratio for each timestep.
    """
    min_ill = daylight_ill.min(axis=0)
    mean_ill = daylight_ill.mean(axis=0)

    return cast(
        "NDArray[np.float32]",
        np.divide(
            min_ill,
            mean_ill,
            out=np.zeros_like(min_ill),
            where=mean_ill > 0.0,
        ),
    )


def uniformity(
    uniformity_map: "NDArray[np.float32]",
) -> float:
    """Calculate average illuminance uniformity.

    Args:
        uniformity_map: Uniformity ratio for each timestep.

    Returns:
        Average uniformity ratio.
    """
    return float(np.mean(uniformity_map))


def daylight_metrics(
    total_ill: "NDArray[np.float32]",
    direct_ill: "NDArray[np.float32]",
    sun_up_hours: "NDArray[np.int64]",
    schedule: "ScheduleInput",
    *,
    da_threshold: float = 300.0,
    udi_lower_threshold: float = 100.0,
    udi_upper_threshold: float = 3000.0,
    ase_threshold: float = 1000.0,
    ase_hours: float = 250.0,
    sda_threshold: float = 0.5,
) -> DaylightMetrics:
    """Calculate annual daylight metrics from result matrices and a schedule.

    Args:
        total_ill: Total illuminance matrix ordered as sensors by sun-up hours.
        direct_ill: Direct illuminance matrix ordered as sensors by sun-up hours.
        sun_up_hours: Sun-up hour indices represented by matrix columns.
        schedule: Occupancy schedule input.
        da_threshold: DA and cDA illuminance threshold in lux.
        udi_lower_threshold: Lower UDI illuminance threshold in lux.
        udi_upper_threshold: Upper UDI illuminance threshold in lux.
        ase_threshold: ASE direct illuminance threshold in lux.
        ase_hours: ASE hour threshold.
        sda_threshold: sDA sensor pass threshold.

    Returns:
        Daylight metric values for one sensor grid.
    """
    if total_ill.shape != direct_ill.shape:
        raise ValueError(
            "Total and direct illuminance matrices must have the same shape. "
            f"Got {total_ill.shape} and {direct_ill.shape}."
        )
    if total_ill.ndim != 2:
        raise ValueError(
            f"Illuminance matrices must be 2D. Got {total_ill.shape}."
        )
    if total_ill.shape[1] != sun_up_hours.shape[0]:
        raise ValueError(
            "Illuminance column count must match sun-up hour count. "
            f"Got {total_ill.shape[1]} and {sun_up_hours.shape[0]}."
        )

    schedule_values = schedule_array(schedule)
    occupied_mask = sun_up_mask(
        schedule_values,
        sun_up_hours,
    )
    occupied_hours = int(np.count_nonzero(schedule_values >= 0.1))
    sun_down_hour_count = sun_down_hours(
        schedule_values,
        sun_up_hours,
    )

    occupied_total_ill = filter_schedule(
        total_ill,
        occupied_mask,
    )
    occupied_direct_ill = filter_schedule(
        direct_ill,
        occupied_mask,
    )

    da_values = da_map(
        occupied_total_ill,
        da_threshold,
        occupied_hours=occupied_hours,
    )
    cda_values = cda_map(
        occupied_total_ill,
        da_threshold,
        occupied_hours=occupied_hours,
    )
    udi_values = udi_map(
        occupied_total_ill,
        udi_lower_threshold,
        udi_upper_threshold,
        occupied_hours=occupied_hours,
    )
    udi_lower_values = udi_low_map(
        occupied_total_ill,
        udi_lower_threshold,
        occupied_hours=occupied_hours,
        sun_down_hours=sun_down_hour_count,
    )
    udi_upper_values = udi_up_map(
        occupied_total_ill,
        udi_upper_threshold,
        occupied_hours=occupied_hours,
    )
    ase_values = ase_map(
        occupied_direct_ill,
        ase_threshold,
    )

    return {
        "da": da_values.tolist(),
        "cda": cda_values.tolist(),
        "udi": udi_values.tolist(),
        "udi_lower": udi_lower_values.tolist(),
        "udi_upper": udi_upper_values.tolist(),
        "ase_hours": ase_values.tolist(),
        "sda": sda(
            da_values,
            sda_threshold,
        ),
        "ase": ase(
            ase_values,
            ase_hours,
        ),
    }


def metrics_for_group(
    aperture_group: "AnnualGroupResult",
    sun_up_hours: "NDArray[np.int64]",
    schedule: "ScheduleInput",
    *,
    da_threshold: float = 300.0,
    udi_lower_threshold: float = 100.0,
    udi_upper_threshold: float = 3000.0,
    ase_threshold: float = 1000.0,
    ase_hours: float = 250.0,
    sda_threshold: float = 0.5,
) -> "GridMetrics":
    """Calculate metrics for every sensor grid in one aperture group.

    Args:
        aperture_group: Annual daylight aperture group result metadata.
        sun_up_hours: Sun-up hour indices represented by matrix columns.
        schedule: Occupancy schedule input.
        da_threshold: DA and cDA illuminance threshold in lux.
        udi_lower_threshold: Lower UDI illuminance threshold in lux.
        udi_upper_threshold: Upper UDI illuminance threshold in lux.
        ase_threshold: ASE direct illuminance threshold in lux.
        ase_hours: ASE hour threshold.
        sda_threshold: sDA sensor pass threshold.

    Returns:
        Sensor grid identifiers mapped to daylight metric values.
    """
    total_files: Dict[str, "Path"] = {
        npy_file.stem: npy_file
        for npy_file in aperture_group["total_npy"]
    }
    direct_files: Dict[str, "Path"] = {
        npy_file.stem: npy_file
        for npy_file in aperture_group["direct_npy"]
    }
    missing_total = sorted(set(direct_files) - set(total_files))
    missing_direct = sorted(set(total_files) - set(direct_files))
    if len(missing_total) > 0 or len(missing_direct) > 0:
        raise ValueError(
            "Total and direct npy files must have matching grid names. "
            f"Missing total: {missing_total}. Missing direct: {missing_direct}."
        )

    return {
        grid_name: daylight_metrics(
            load_npy(total_files[grid_name]),
            load_npy(direct_files[grid_name]),
            sun_up_hours,
            schedule,
            da_threshold=da_threshold,
            udi_lower_threshold=udi_lower_threshold,
            udi_upper_threshold=udi_upper_threshold,
            ase_threshold=ase_threshold,
            ase_hours=ase_hours,
            sda_threshold=sda_threshold,
        )
        for grid_name in sorted(total_files)
    }


def annual_metrics(
    result: "AnnualResult",
    schedule: "ScheduleInput",
    *,
    sun_up_hours: Optional["NDArray[np.int64]"] = None,
    da_threshold: float = 300.0,
    udi_lower_threshold: float = 100.0,
    udi_upper_threshold: float = 3000.0,
    ase_threshold: float = 1000.0,
    ase_hours: float = 250.0,
    sda_threshold: float = 0.5,
) -> "AnnualMetrics":
    """Calculate metrics for every aperture group and sensor grid.

    Args:
        result: Annual daylight simulation result metadata.
        schedule: Occupancy schedule input.
        sun_up_hours: Optional sun-up hour indices. If omitted, they are read
            from the recipe results folder.
        da_threshold: DA and cDA illuminance threshold in lux.
        udi_lower_threshold: Lower UDI illuminance threshold in lux.
        udi_upper_threshold: Upper UDI illuminance threshold in lux.
        ase_threshold: ASE direct illuminance threshold in lux.
        ase_hours: ASE hour threshold.
        sda_threshold: sDA sensor pass threshold.

    Returns:
        Aperture groups mapped to sensor grid daylight metric values.
    """
    if sun_up_hours is None:
        sun_up_hours = load_sun_up_hours(result["results"] / "sun-up-hours.txt")

    return {
        group_name: metrics_for_group(
            aperture_group,
            sun_up_hours,
            schedule,
            da_threshold=da_threshold,
            udi_lower_threshold=udi_lower_threshold,
            udi_upper_threshold=udi_upper_threshold,
            ase_threshold=ase_threshold,
            ase_hours=ase_hours,
            sda_threshold=sda_threshold,
        )
        for group_name, aperture_group in result["aperture_groups"].items()
    }
