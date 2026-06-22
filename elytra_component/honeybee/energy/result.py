from __future__ import annotations
from typing import (
    Dict,
    List,
    Optional,
    Sequence,
    Tuple,
    Union,
    cast,
    TYPE_CHECKING,
)
if TYPE_CHECKING:
    from os import PathLike
    from .typing import (
        SqlResultItem,
        SqlResultList,
        EnergyOutputResult,
        EnergyResultMap,
        FaceResultMap,
        ComfortResultMap,
        EnergyDataCollection,
        EUIResult,
        HVACSizingCell,
        HVACSizingResult,
        TabularCell,
        TabularDataResult,
        ZoneSizingResult,
    )

from honeybee.search import filter_array_by_keywords
from honeybee_energy.result.rdd import RDD
from honeybee_energy.result.zsz import ZSZ
from honeybee_energy.result.eui import eui_from_sql
from ladybug.datacollection import BaseCollection
from ladybug.sql import SQLiteResult
from pathlib import Path
from tqdm import tqdm

import platform
import numpy as np

from .config import (
    ENERGY_OUTPUTS,
    FACE_OUTPUTS,
    OPAQUE_ENERGY_FLOW_OUTPUTS,
    WINDOW_LOSS_ENERGY_OUTPUTS,
    WINDOW_GAIN_ENERGY_OUTPUTS,
    FaceResultName,
    COMFORT_OUTPUTS,
)


def load_custom_result(
    sql_path: Union[str, "PathLike[str]"],
    output_names: Sequence[str],
) -> "EnergyOutputResult":
    """Load custom EnergyPlus time-series outputs from an SQL file.

    Args:
        sql_path: EnergyPlus SQL result file.
        output_names: EnergyPlus output variable names to request.

    Returns:
        Float32 array for scalar values, or Ladybug data collections for
        time-series values.
    """
    sql_obj = SQLiteResult(str(Path(sql_path)))
    res = cast(
        "SqlResultList",
        sql_obj.data_collections_by_output_name(output_names),
    )
    return format_sql_result(res)


def load_result_dictionary(
    rdd_path: Union[str, "PathLike[str]"],
    keywords: Sequence[str] = (),
    join_words: bool = False,
) -> Tuple[str, ...]:
    """Read requestable EnergyPlus output names from an RDD file.

    Args:
        rdd_path: EnergyPlus RDD result dictionary file.
        keywords: Optional keywords used to filter output names.
        join_words: Whether each keyword string should be treated as a phrase.

    Returns:
        EnergyPlus output names that can be used by custom simulation output.
    """
    rdd = RDD(str(Path(rdd_path)))
    raw_output_names = rdd.output_names
    if raw_output_names is None:
        return ()

    output_names = cast(
        Tuple[str, ...],
        tuple(raw_output_names),
    )
    if len(keywords) == 0:
        return output_names

    return cast(
        Tuple[str, ...],
        tuple(
            filter_array_by_keywords(
                output_names,
                keywords,
                not join_words,
            )
        ),
    )


def load_tabular_data(
    sql_path: Union[str, "PathLike[str]"],
    table_name: str,
) -> "TabularDataResult":
    """Load a Summary Report table from an EnergyPlus SQL file.

    Args:
        sql_path: EnergyPlus SQL result file.
        table_name: Summary Report table name.

    Returns:
        Table values, row names, and column names.
    """
    sql_obj = SQLiteResult(str(Path(sql_path)))
    results = cast(
        Dict[str, Sequence["TabularCell"]],
        sql_obj.tabular_data_by_name(table_name),
    )
    return {
        "values": tuple(
            tuple(row)
            for row in results.values()
        ),
        "row_names": tuple(results.keys()),
        "column_names": tuple(
            cast(
                Sequence[str],
                sql_obj.tabular_column_names(table_name),
            )
        ),
    }


def load_hvac_sizing(
    sql_path: Union[str, "PathLike[str]"],
    component_type: Optional[str] = None,
) -> "HVACSizingResult":
    """Load zone peak loads and HVAC component sizing results from SQL.

    Args:
        sql_path: EnergyPlus SQL result file.
        component_type: Optional HVAC component type used to filter components.

    Returns:
        Zone peak cooling and heating loads, component types, component
        property names, and component sizing values.
    """
    sql_obj = SQLiteResult(str(Path(sql_path)))
    zone_cooling_sizes = sql_obj.zone_cooling_sizes
    zone_heating_sizes = sql_obj.zone_heating_sizes

    if component_type is None:
        component_types = tuple(
            cast(
                Sequence[str],
                sql_obj.component_types,
            )
        )
        component_sizes = sql_obj.component_sizes
    else:
        component_types = (component_type,)
        component_sizes = sql_obj.component_sizes_by_type(component_type)

    return {
        "zone_names": tuple(
            zone_size.zone_name
            for zone_size in zone_cooling_sizes
        ),
        "zone_peak_cool": tuple(
            float(zone_size.calculated_design_load)
            for zone_size in zone_cooling_sizes
        ),
        "zone_peak_heat": tuple(
            float(zone_size.calculated_design_load)
            for zone_size in zone_heating_sizes
        ),
        "component_types": component_types,
        "component_properties": tuple(
            tuple(
                str(description)
                for description in component_size.descriptions
            )
            for component_size in component_sizes
        ),
        "component_values": tuple(
            tuple(
                cast(
                    "HVACSizingCell",
                    value,
                )
                for value in component_size.values
            )
            for component_size in component_sizes
        ),
    }


def load_zone_sizing(
    zsz_path: Union[str, "PathLike[str]"],
) -> "ZoneSizingResult":
    """Load zone sizing design-day cooling and heating load collections.

    Args:
        zsz_path: EnergyPlus zone sizing CSV file.

    Returns:
        Cooling load collections and heating load collections.
    """
    zsz = ZSZ(str(Path(zsz_path)))
    return (
        tuple(
            cast(
                List["EnergyDataCollection"],
                zsz.cooling_load_data,
            )
        ),
        tuple(
            cast(
                List["EnergyDataCollection"],
                zsz.heating_load_data,
            )
        ),
    )


def format_sql_result(
    res: "SqlResultList",
) -> "EnergyOutputResult":
    """Format a Honeybee SQL query result.

    Args:
        res: Raw SQL query result values from Ladybug SQL.

    Returns:
        Float32 array for scalar values, or Ladybug data collections for
        time-series values.
    """
    if not res:
        return np.asarray(
            [],
            dtype=np.float32,
        )

    if isinstance(res[0], float):
        return np.asarray(
            res,
            dtype=np.float32,
        )

    if isinstance(res[0], BaseCollection):
        return cast(
            List["EnergyDataCollection"],
            res,
        )

    raise ValueError(
        f"Unexpected result type: {type(res[0])}"
    )

def load_energy_sql_room_results(
    sql_path: Union[str, "PathLike[str]"],
    is_processing_print: bool = True,
) -> "EnergyResultMap":
    """Load room-level energy use results from an EnergyPlus SQL file.

    Args:
        sql_path: EnergyPlus SQL result file.
        is_processing_print: Whether to print missing output messages.

    Returns:
        Energy result names mapped to numeric arrays or Ladybug data
        collections.
    """
    sql_path = Path(sql_path)

    if not sql_path.exists():
        raise FileNotFoundError(f"SQL file not found: {sql_path}")

    if not sql_path.is_file():
        raise ValueError(
            f"Expected a SQL file,"
            f" but got a directory: {sql_path}"
        )

    if sql_path.suffix.lower() not in {".sql", }:
        raise ValueError(f"Expected SQL file, got: {sql_path.suffix}")

    if platform.system() != "Windows":
        raise NotImplementedError(
            "This function is only implemented for Windows."
        )

    sql_obj = SQLiteResult(str(sql_path))

    results: "EnergyResultMap" = {}

    for r_name, o_name in tqdm(
        ENERGY_OUTPUTS.items(),
        desc="Loading Energy Results",
        leave=False,
    ):
        # r_name: result name
        # o_name: output name
        try:
            res = cast(
                "SqlResultList",
                sql_obj.data_collections_by_output_name(o_name),
            )
        except Exception as e:
            tqdm.write(
                f"❗Error occurred while loading result '{r_name}': {e}"
            )
            continue

        if not res:
            if is_processing_print:
                tqdm.write(
                    f"❕Result '{r_name}' has no data for output names: {o_name}"
                )
            continue

        new_res = format_sql_result(res)
        results[r_name] = new_res

    return results


def _subtract_sql_result_item(
    gain: "SqlResultItem",
    loss: "SqlResultItem",
) -> "SqlResultItem":
    """Subtract matching scalar or collection SQL result values.

    Args:
        gain: Window gain result item.
        loss: Window loss result item.

    Returns:
        Energy flow item computed as gain minus loss.
    """
    if isinstance(gain, float) and isinstance(loss, float):
        return gain - loss

    if isinstance(gain, BaseCollection) and isinstance(loss, BaseCollection):
        return cast(
            "SqlResultItem",
            gain - loss,
        )

    raise ValueError(
        f"Expected gain/loss to have the same type,"
        f" but got {type(gain)} and {type(loss)}."
    )

def load_energy_sql_faces_results(
    sql_path: Union[str, "PathLike[str]"],
    is_processing_print: bool = True,
) -> "FaceResultMap":
    """Load face temperature and energy-flow results from an SQL file.

    Args:
        sql_path: EnergyPlus SQL result file.
        is_processing_print: Whether to print missing output messages.

    Returns:
        Face result names mapped to numeric arrays or Ladybug data collections.
    """
    sql_path = Path(sql_path)

    if not sql_path.exists():
        raise FileNotFoundError(f"SQL file not found: {sql_path}")

    if not sql_path.is_file():
        raise ValueError(
            f"Expected a SQL file,"
            f" but got a directory: {sql_path}"
        )

    if sql_path.suffix.lower() not in {".sql", }:
        raise ValueError(f"Expected SQL file, got: {sql_path.suffix}")

    if platform.system() != "Windows":
        raise NotImplementedError(
            "This function is only implemented for Windows."
        )

    sql_obj = SQLiteResult(str(sql_path))

    results: "FaceResultMap" = {}
    for r_name, o_name in tqdm(
        FACE_OUTPUTS.items(),
        desc="Loading Face Results",
        leave=False
    ):
        try:
            res = cast(
                "SqlResultList",
                sql_obj.data_collections_by_output_name(o_name),
            )
        except Exception as e:
            tqdm.write(
                f"Error occurred while loading result '{r_name}': {e}"
            )
            continue

        if not res:
            if is_processing_print:
                tqdm.write(
                    f"Result '{r_name}' has no data for output names: {o_name}"
                )
            continue

        results[r_name] = format_sql_result(res)

    try:
        opaque_energy_flow = cast(
            "SqlResultList",
            sql_obj.data_collections_by_output_name(
                OPAQUE_ENERGY_FLOW_OUTPUTS
            )
        )
        window_loss = cast(
            "SqlResultList",
            sql_obj.data_collections_by_output_name(
                WINDOW_LOSS_ENERGY_OUTPUTS,
            )
        )
        window_gain = cast(
            "SqlResultList",
            sql_obj.data_collections_by_output_name(
                WINDOW_GAIN_ENERGY_OUTPUTS
            )
        )
    except Exception as e:
        tqdm.write(
            f"Error occurred while loading face energy flow results: {e}"
        )
        return results

    window_energy_flow: "SqlResultList" = []

    if len(window_gain) == len(window_loss):
        for gain, loss in zip(window_gain, window_loss):
            window_energy_flow.append(
                _subtract_sql_result_item(
                    gain,
                    loss
                )
            )
    elif is_processing_print:
        tqdm.write(
            f"Window gain/loss length mismatch: "
            f"gain={len(window_gain)}, loss={len(window_loss)}"
        )

    face_energy_flow: "SqlResultList" = [
        *opaque_energy_flow,
        *window_energy_flow,
    ]

    if face_energy_flow:
        results[FaceResultName.FACE_ENERGY_FLOW] = format_sql_result(
            face_energy_flow
        )

    return results

def load_energy_sql_comfort_results(
    sql_path: Union[str, "PathLike[str]"],
    is_processing_print: bool = True,
) -> "ComfortResultMap":
    """Load zone comfort results from an EnergyPlus SQL file.

    Args:
        sql_path: EnergyPlus SQL result file.
        is_processing_print: Whether to print missing output messages.

    Returns:
        Comfort result names mapped to numeric arrays or Ladybug data
        collections.
    """
    sql_path = Path(sql_path)

    if not sql_path.exists():
        raise FileNotFoundError(f"SQL file not found: {sql_path}")

    if not sql_path.is_file():
        raise ValueError(
            f"Expected a SQL file,"
            f" but got a directory: {sql_path}"
        )

    if sql_path.suffix.lower() not in {".sql", }:
        raise ValueError(f"Expected SQL file, got: {sql_path.suffix}")

    if platform.system() != "Windows":
        raise NotImplementedError(
            "This function is only implemented for Windows."
        )

    sql_obj = SQLiteResult(str(sql_path))
    results: "ComfortResultMap" = {}

    for r_name, o_name in COMFORT_OUTPUTS.items():
        try:
            res = cast(
                "SqlResultList",
                sql_obj.data_collections_by_output_name(o_name),
            )
        except Exception as e:
            tqdm.write(
                f"Error occurred while loading comfort result '{r_name}': {e}"
            )
            continue

        if not res:
            if is_processing_print:
                tqdm.write(
                    f"Result '{r_name}' has no data for output names: {o_name}"
                )
            continue

        results[r_name] = format_sql_result(res)

    return results

def load_eui(
    sql_path: Union[str, "PathLike[str]"],
) -> "EUIResult":
    """Load Energy Use Intensity summary values from an SQL file.

    Args:
        sql_path: EnergyPlus SQL result file.

    Returns:
        EUI summary values including floor areas, total energy, and end uses.
    """

    sql_path = Path(sql_path)
    if not sql_path.exists():
        raise FileNotFoundError(
            f"SQL file not found: {sql_path}"
        )

    if not sql_path.is_file():
        raise ValueError(
            f"Expected a SQL file, but got a directory: {sql_path}"
        )

    if sql_path.suffix.lower() not in {".sql", ".db", ".sqlite"}:
        raise ValueError(
            f"Expected SQL file, got: {sql_path.suffix}"
        )

    result = eui_from_sql(str(sql_path))
    return cast(
        "EUIResult",
        result,
    )
