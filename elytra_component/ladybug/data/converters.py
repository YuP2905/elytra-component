from __future__ import annotations
from typing import (
    List,
    Tuple,
    Union,
    Sequence,
    Optional,
    cast,
    TYPE_CHECKING,
)
if TYPE_CHECKING:
    from ladybug.datacollection import (
        Header,
    )
    from ladybug.dt import DateTime

    from ...ladybug.typing import (
        LadybugDataCollection,
        DataInterval
    )


from ladybug.datacollection import (
    HourlyContinuousCollection,
    DailyCollection,
    MonthlyCollection,
    MonthlyPerHourCollection,
    HourlyDiscontinuousCollection,
)
import ladybug.datatype
from ladybug.datatype.base import DataTypeBase
from ladybug.datatype.generic import GenericType
from ladybug.analysisperiod import AnalysisPeriod

def construct_data(
    header: Header,
    values: Sequence[float], # Tuple[float, ...],
    interval: DataInterval = "hourly",
) -> "LadybugDataCollection":
    """
    Construct a Ladybug data collection from header and values.
    Args:
        header: A Ladybug header object describing the metadata of the data collection.
        values: A sequence of numerical values for the data collection.
        interval: Text to indicate the time interval of the data collection, which
            determines the type of collection that is output. (Default: hourly).
            Choose from the following:
                - hourly
                - daily
                - monthly
                - monthly-per-hour
            Note that the "hourly" input is also used to represent sub-hourly
            intervals (in this case, the timestep of the analysis period
            must not be 1).
    Returns:
        data: A Ladybug data collection object.
    """
    interval_value = interval.lower()

    aper = header.analysis_period
    if interval_value == "hourly":

        if aper.st_hour == 0 and aper.end_hour == 23:
            return HourlyContinuousCollection(
                header,
                values
            )

        return HourlyDiscontinuousCollection(
            header,
            values,
            cast(
                Tuple["DateTime"],
                aper.datetimes
            )
        )
    elif interval_value == "monthly":
        return MonthlyCollection(
            header,
            values,
            aper.months_int
        )
    elif interval_value == "daily":
        return DailyCollection(
            header,
            values,
            aper.doys_int
        )
    elif interval_value == "monthly-per-hour":
        return MonthlyPerHourCollection(
            header,
            values,
            cast(
                List[Tuple[int, ...]],
                aper.months_per_hour
            )
        )
    else:
        raise ValueError(
            f"Interval of '{interval_value}' is not supported. Please use one of "
            f"'hourly', 'daily', 'monthly', or 'monthly-per-hour'."
        )

def construct_data_type(
    name: str,
    unit: str,
    cumulative: bool = False,
    categories: Optional[Sequence[str]] = None,
) -> GenericType:
    """
    Construct a Ladybug DataType to be used in the header of a ladybug DataCollection.
    Args:
        name: A name for the data type as a string.
        unit: A unit for the data type as a string.
        cumulative: Boolean to tell whether the data type can be cumulative when it
            is represented over time (True) or it can only be averaged over time
            to be meaningful (False).
        categories: An optional list of text for categories to be associated with
            the data type. These categories will show up in the legend whenever
            data with this data type is visualized. The input should be
            text strings with a category number (integer) and name separated
            by a colon. For example:

            .    -1: Cold
            .     0: Neutral
            .     1: Hot

    Returns:
        type: A Ladybug DataType object that can be assigned to the header
            of a Ladybug DataCollection.
    """
    unit_descr = None

    if categories:
        unit_descr = {}
        for prop in categories:
            try:
                k, v = prop.split(":", 1)
                unit_descr[int(k.strip())] = v.strip()
            except Exception as e:
                raise ValueError(
                    f"Category '{prop}' is not in the correct format. Please use "
                    f"text strings with a category number (integer) and name "
                    f"separated by a colon. For example: '-1: Cold'."
                ) from e

    if cumulative:
        return GenericType(
            name,
            unit,
            unit_descr=unit_descr,
            point_in_time=False,
            cumulative=True,
        )
    return GenericType(
        name,
        unit,
        unit_descr=unit_descr,
    )

def construct_header(
    data_type: Union[str, DataTypeBase],
    unit: Optional[str] = None,
    a_period: Optional[AnalysisPeriod] = None,
    metadata: Optional[Sequence[str]] = None,
) -> Header:
    """
    Construct a Ladybug Header to be used to create a ladybug DataCollection.
    Args:
        data_type: Text representing the type of data (e.g. Temperature). A full list
            of acceptable inputs can be seen by checking the all_u output of
            the "LB Unit Converter" component. This input can also be a custom
            DataType object that has been created with the "construct_data_type" function.
        unit: Units of the data_type (e.g. C). Default is to use the
            base unit of the connected_data_type.
        a_period: A Ladybug AnalysisPeriod object. (Default in None)
        metadata: Optional metadata to be associated with the Header. The input should
            be a list of text strings with a property name and value for the
            property separated by a colon. For example:
        .    source: TMY
        .    city: New York
        .    country: USA

    Returns:
        header: A Ladybug Header object.
    """

    accepted_types = "\n".join(cast(Tuple[str], ladybug.datatype.BASETYPES))
    msg = (
        "The data_type is not recognized.\n"
        "Make your own with construct_data_type() or choose from the following:\n"
        f"{accepted_types}"
    )

    data_type_base: DataTypeBase
    if isinstance(data_type, DataTypeBase):
        data_type_base = data_type
    elif isinstance(data_type, str):
        data_type_key = data_type.replace(" ", "").lower()
        try:
            data_type_base = ladybug.datatype.TYPESDICT[data_type_key]()
        except KeyError:
            for k in ladybug.datatype.TYPESDICT:
                k = cast(str, k)
                if k.lower() == data_type_key:
                    data_type_base = ladybug.datatype.TYPESDICT[k]()
                    break
            else:
                raise TypeError(msg)
    else:
        raise TypeError(msg)

    unit = unit or data_type_base.units[0]
    a_period = a_period or AnalysisPeriod()

    metadata_dict = {}
    if metadata:
        for prop in metadata:
            try:
                k, v = prop.split(":", 1)
                metadata_dict[k.strip()] = v.strip()
            except Exception as e:
                raise ValueError(
                    f"Metadata '{prop}' is not in the correct format. Please use "
                    f"text strings with a property name and value separated by a "
                    f"colon. For example: 'source: TMY'."
                ) from e

    return Header(
        cast(DataTypeBase, data_type_base),
        cast(str, unit),
        a_period,
        metadata_dict
    )
