from __future__ import annotations
from typing import (
    List,
    Tuple,
    Union,
    cast,
    TYPE_CHECKING,
)
from collections.abc import Mapping, Sequence

from ladybug.datacollection import (
    BaseCollection,
    MonthlyPerHourCollection,
    HourlyContinuousCollection,
    HourlyDiscontinuousCollection,
)
from ladybug.dt import DateTime
import numpy as np

if TYPE_CHECKING:
    from ladybug.analysisperiod import AnalysisPeriod
    from ladybug.dt import DateTime
    from ladybug.header import Header
    from ladybug.sunpath import Sun
    from ladybug.datatype.base import DataTypeBase
    from numpy.typing import NDArray

    from ..typing import (
        DataDateTimeValue,
        HeaderMetadataValue,
        HourlyDataCollection,
        LadybugDataCollection,
    )



def deconstruct_data(
    data: BaseCollection,
) -> Tuple["Header", Tuple[float, ...]]:
    """Deconstruct a Ladybug data collection into header and values.

    Args:
        data: A Ladybug data collection.

    Returns:
        A tuple containing:
        - header: The collection header.
        - values: The collection values converted to float.
    """
    return (
        data.header,
        tuple(
            float(value)
            for value in cast(Sequence[Union[float, int]], data.values)
        ),
    )


def deconstruct_header(
    header: "Header",
) -> Tuple["DataTypeBase", str, "AnalysisPeriod", Tuple[str, ...]]:
    """Deconstruct a Ladybug header into its fields.

    Args:
        header: A Ladybug header.

    Returns:
        A tuple containing:
        - data_type: Ladybug data type.
        - unit: Header unit.
        - analysis_period: Header analysis period.
        - metadata: Metadata entries formatted as ``key: value``.
    """
    metadata_values = cast("Mapping[str, HeaderMetadataValue]", header.metadata)
    metadata = tuple(
        f"{key}: {value}"
        for key, value in metadata_values.items()
    )
    return (
        header.data_type,
        header.unit,
        header.analysis_period,
        metadata,
    )


def data_datetimes(
    data: "LadybugDataCollection",
) -> Tuple["DataDateTimeValue", ...]:
    """Return the hour, day, or month values associated with collection values.

    Args:
        data: Ladybug data collection.

    Returns:
        DateTime, HOY, or monthly hour values associated with the collection.
    """
    if isinstance(data, HourlyDiscontinuousCollection):
        datetimes = cast(Sequence["DateTime"], data.datetimes)
        return tuple(
            dt.hoy
            for dt in datetimes
        )

    if isinstance(data, MonthlyPerHourCollection):
        datetimes = cast(Sequence["DateTime"], data.datetimes)
        return tuple(
            DateTime(
                month=dt.month,
                day=1,
                hour=dt.hour,
                minute=dt.minute,
            ).hoy
            for dt in datetimes
        )

    if isinstance(data, HourlyContinuousCollection):
        datetimes = cast(Sequence["DateTime"], data.datetimes)
        return tuple(
            dt.hoy
            for dt in datetimes
        )

    return tuple(
        cast(Sequence["DateTime"], data.datetimes)
    )


def filter_data_collection_by_statement(
    data: Union[BaseCollection, Sequence[BaseCollection]],
    statement: str,
) -> Union[BaseCollection, Tuple[BaseCollection, ...]]:
    """Filter one or more Ladybug data collections by a statement.

    Args:
        data: One collection or aligned collections.
        statement: Ladybug conditional statement.

    Returns:
        One filtered collection when one collection is supplied, otherwise a
        tuple of filtered collections.
    """
    data_collections = (data,) if isinstance(data, BaseCollection) else tuple(data)
    filtered_data = cast(
        List["BaseCollection"],
        BaseCollection.filter_collections_by_statement(
            data_collections,
            statement,
        ),
    )

    return filtered_data[0] if len(filtered_data) == 1 else tuple(filtered_data)


def align_hoys_by_hourly_data_collection(
    hoys: Union[Sequence[Union[float, int]], float, int],
    data: Union["HourlyDataCollection", Sequence["HourlyDataCollection"]],
) -> "NDArray[np.float64]":
    """Return HOYs that exist in one or more aligned hourly collections.

    Args:
        hoys: One HOY or multiple HOY values.
        data: One hourly collection or aligned hourly collections.

    Returns:
        Float64 array of HOY values that exist in the hourly collection data.
    """
    hoy_values = (hoys,) if isinstance(hoys, (float, int)) else tuple(hoys)
    if isinstance(
        data,
        (
            HourlyContinuousCollection,
            HourlyDiscontinuousCollection,
        ),
    ):
        data_collections: Tuple["HourlyDataCollection", ...] = (data,)
    else:
        data_collections = tuple(data)

    first_data = data_collections[0]
    if len(data_collections) > 1:
        is_aligned = all(
            first_data.is_collection_aligned(data_collection)
            for data_collection in data_collections[1:]
        )
        if not is_aligned:
            raise ValueError(
                "The data collections are not aligned."
            )

    first_data_datetimes = cast(Sequence["DateTime"], first_data.datetimes)
    data_hoys = {
        datetime.hoy
        for datetime in first_data_datetimes
    }
    aligned_hoys = tuple(
        hoy
        for hoy in hoy_values
        if hoy in data_hoys
    )

    return np.asarray(
        aligned_hoys,
        dtype=np.float64,
    )


def align_hourly_data_collection_by_suns(
    data: Union["HourlyDataCollection", Sequence["HourlyDataCollection"]],
    suns: Sequence["Sun"],
) -> Union["HourlyDataCollection", Tuple["HourlyDataCollection", ...]]:
    """Filter hourly collections to the datetimes represented by suns.

    Args:
        data: One hourly collection or aligned hourly collections.
        suns: Sun objects whose datetimes define the filter.

    Returns:
        One filtered hourly collection when one collection is supplied,
        otherwise a tuple of filtered hourly collections.
    """
    if isinstance(
        data,
        (
            HourlyContinuousCollection,
            HourlyDiscontinuousCollection,
        ),
    ):
        data_collections: Tuple["HourlyDataCollection", ...] = (data,)
    else:
        data_collections = tuple(data)

    sun_moys = tuple(
        cast("DateTime", sun.datetime).moy
        for sun in suns
    )

    aligned_data: List["HourlyDataCollection"] = []
    for data_collection in data_collections:
        aligned_data.append(
            data_collection.filter_by_moys(sun_moys)
        )

    return aligned_data[0] if len(aligned_data) == 1 else tuple(aligned_data)
