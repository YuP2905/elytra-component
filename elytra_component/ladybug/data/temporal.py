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
    """
    Create an Analysis Period to describe a slice of time during the year.
        Args:
            start_month: Start month (1-12).
            start_day: Start day (1-31).
            start_hour: Start hour (0-23).
            end_month: End month (1-12).
            end_day: End day (1-31).
            end_hour: End hour (0-23).
            timestep: An integer number for the number of time steps per hours.
                Acceptable inputs include: 1, 2, 3, 4, 5, 6, 10, 12, 15, 20, 30, 60

        Returns:
            period: Analysis period.
            hoys: List of dates in this analysis period.
            dates: List of hours of the year in this analysis period.
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