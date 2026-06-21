from __future__ import annotations
from typing import (
    Tuple,
    TYPE_CHECKING,
)
if TYPE_CHECKING:
    from ladybug.dt import datetime

from ladybug.dt import DateTime
from ladybug.analysisperiod import AnalysisPeriod


def construct_analysis_period(
    start_month: int = 1,
    start_day: int = 1,
    start_hour: int = 0,
    end_month: int = 12,
    end_day: int = 31,
    end_hour: int = 23,
    timestep: int = 1,
) -> Tuple[AnalysisPeriod, Tuple[int, ...], Tuple["datetime", ...]]:
    """Create an analysis period for a slice of time during the year.

    Args:
        start_month: Start month.
        start_day: Start day.
        start_hour: Start hour.
        end_month: End month.
        end_day: End day.
        end_hour: End hour.
        timestep: Number of timesteps per hour.

    Returns:
        A tuple containing the analysis period, HOYs, and datetimes.
    """
    period = AnalysisPeriod(
        start_month,
        start_day,
        start_hour,
        end_month,
        end_day,
        end_hour,
        timestep,
    )

    return (
        period,
        period.hoys,
        period.datetimes,
    )

def calculate_hoy(
    month: int = 9,
    day: int = 21,
    hour: int = 12,
    minute: int = 0,
) -> Tuple[float, int, DateTime]:
    """Calculate HOY, DOY, and DateTime from a date and time.

    Args:
        month: Month of year.
        day: Day of month.
        hour: Hour of day.
        minute: Minute of hour.

    Returns:
        A tuple containing HOY, DOY, and Ladybug DateTime.
    """
    date = DateTime(
        month,
        day,
        hour,
        minute,
    )

    return (
        date.hoy,
        date.doy,
        date,
    )
