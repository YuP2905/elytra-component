from __future__ import annotations

from typing import (
    List,
    Tuple,
    Union,
    Sequence,
    Optional,
    Literal,
    cast,
    TYPE_CHECKING,
)

if TYPE_CHECKING:
    from ladybug_geometry.geometry3d.arc import Arc3D
    from ladybug_geometry.geometry3d.pointvector import Point3D
    from ladybug_geometry.geometry3d.polyline import Polyline3D
    from ladybug.datacollection import (
        HourlyContinuousCollection,
        HourlyDiscontinuousCollection,
        Header
    )
    from ladybug.legend import LegendParameters
    from matplotlib.axes import Axes
    from mpl_toolkits.mplot3d import Axes3D
    from numpy.typing import NDArray
    from ..typing import ColorbarOrientation


from ladybug.datacollection import HourlyContinuousCollection
from ladybug.compass import Compass
from ladybug.graphic import GraphicContainer
import matplotlib.pyplot as plt
import numpy as np

from ..array import points_vectors_2_array
from ._matplotlib import (
    color_to_mpl,
    data_collection_title,
    plot_compass,
    plot_colorbar,
    plot_coordinates,
    plot_points,
)


def plot_sunpath(
    sun_points: Sequence["Point3D"],
    sun_polylines: Sequence["Polyline3D"],
    sun_arcs: Sequence["Arc3D"],
    filtered_data: Union["HourlyContinuousCollection", "HourlyDiscontinuousCollection", None] = None,
    projection: Literal["Orthographic", "Stereographic"] = "Orthographic",
    legend_parameters: Optional["LegendParameters"] = None,
    *,
    ax: Optional["Axes"] = None,
    show_colorbar: bool = True,
    show_title: bool = True,
    colorbar_discrete: bool = True,
    colorbar_orientation: Optional["ColorbarOrientation"] = None,
    linewidth: float = 1,
    linecolor: str = "gray",
) -> Union["Axes", "Axes3D"]:
    sun_points_arr: "NDArray[np.float64]" = points_vectors_2_array(
        sun_points
    )  # shape (n, 3)
    if sun_points_arr.ndim != 2 or sun_points_arr.shape[1] != 3:
        raise ValueError(
            "sun_points_arr must have shape (n, 3)."
        )

    sun_polylines_pts: List["NDArray[np.float64]"] = []
    for polyline in sun_polylines:
        polyline_points_arr = points_vectors_2_array(
            cast(Tuple["Point3D"], polyline.vertices)
        )  # shape (m, 3)

        sun_polylines_pts.append(polyline_points_arr)

    sun_arcs_pts: List["NDArray[np.float64]"] = []
    for arc in sun_arcs:
        arc_points_arr = points_vectors_2_array(
            cast(Tuple["Point3D"], cast("Polyline3D", arc.to_polyline(32)).vertices)
        )  # shape (m, 3)

        sun_arcs_pts.append(arc_points_arr)

    data_values = np.asarray(
        cast(Tuple[float], filtered_data.values),
        dtype=np.float64,
    ) if filtered_data is not None else None

    if data_values is not None and len(data_values) != len(sun_points_arr):
        raise ValueError(
            f"The number of filtered data points"
            f" ({len(data_values)}) does not match the number of sun points ({len(sun_points_arr)})."
            f"Plz use `align_hourly_data_collection_by_suns` to align the data with the sun points."
        )

    if ax is None:
        fig = plt.figure()
        ax = fig.add_subplot(
            111,
            projection="3d" if projection == "Stereographic" else None,
        )
        ax = cast(Union["Axes", "Axes3D"], ax)

    spatial = projection == "Stereographic"
    compass = Compass()

    if data_values is not None:
        data_collection = cast(
            Union["HourlyContinuousCollection", "HourlyDiscontinuousCollection"],
            filtered_data,
        )
        header = cast("Header", data_collection.header)
        graphic = GraphicContainer(
            tuple(
                float(value)
                for value in data_values
            ),
            compass.min_point3d(),
            compass.max_point3d(),
            legend_parameters,
            header.data_type,
            cast(str, header.unit)
        )
        point_colors = [
            color_to_mpl(color) if color is not None else "gray"
            for color in graphic.value_colors
        ]
        plot_points(
            ax,
            sun_points_arr,
            spatial=spatial,
            size=5,
            color=point_colors,
        )

        if show_colorbar:
            plot_colorbar(
                ax,
                graphic.legend,
                discrete=colorbar_discrete,
                orientation=colorbar_orientation,
            )
        if show_title:
            ax.set_title(
                data_collection_title(
                    data_collection,
                    include_analysis_period=False,
                ),
                loc="left",
                fontsize=8.0,
            )

    for pt_arr in sun_polylines_pts:
        plot_coordinates(
            ax,
            pt_arr,
            spatial=spatial,
            color=linecolor,
            linewidth=linewidth,
        )

    for pt_arr in sun_arcs_pts:
        plot_coordinates(
            ax,
            pt_arr,
            spatial=spatial,
            color=linecolor,
            linewidth=linewidth,
        )

    plot_compass(
        ax,
        compass,
        spatial=spatial,
        show_boundary=True,
        color=linecolor,
        linewidth=linewidth,
    )

    if projection == "Orthographic":
        cast("Axes", ax).set_aspect(
            "equal",
            adjustable="box",
        )
    else:
        cast("Axes3D", ax).set_box_aspect((1, 1, 0.5))
    return ax
