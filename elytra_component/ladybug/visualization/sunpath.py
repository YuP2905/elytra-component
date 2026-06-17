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
    from ladybug_geometry.geometry3d.polyline import Polyline3D
    from ladybug.datacollection import (
        HourlyContinuousCollection,
        HourlyDiscontinuousCollection,
        Header
    )
    from matplotlib.axes import Axes
    from matplotlib.figure import Figure
    from mpl_toolkits.mplot3d import Axes3D
    from matplotlib.colors import LinearSegmentedColormap
    from numpy.typing import NDArray


from ladybug.datacollection import HourlyContinuousCollection
from ladybug_geometry.geometry3d.pointvector import Point3D
import matplotlib.pyplot as plt
import numpy as np

from ...ladybug.utils import points_vectors_2_array
from .config import VISUALIZATION_CONFIG
from ...ladybug.config import LADYBUG_CONFIG


def _plot_compass(
    ax: Union["Axes", "Axes3D"],
    projection: Literal["Orthographic", "Stereographic"],
    scale: float,
    *,
    linewidth: float,
    linecolor: str
) -> None:
    dims = 2 if projection == "Orthographic" else 3

    outer_radius = VISUALIZATION_CONFIG.DEFAULT_RADIUS * scale
    inner_radius = outer_radius - VISUALIZATION_CONFIG.DEFAULT_OFFSET * scale

    theta = np.linspace(
        0.0,
        2.0 * np.pi,
        361,
        dtype=np.float32,
    )

    sin_theta = np.sin(theta)
    cos_theta = np.cos(theta)
    zero_theta = np.zeros_like(theta)

    for radius in (outer_radius, inner_radius):
        circle_arr = np.stack(
            (
                radius * sin_theta,
                radius * cos_theta,
                zero_theta,
            ),
            axis=-1,
        )[:, :dims]

        ax.plot(
            *circle_arr.T,
            color=linecolor,
            linewidth=linewidth,
            zorder=0,
        )

    labels = (
        "N",
        "NNE",
        "NE",
        "ENE",
        "E",
        "ESE",
        "SE",
        "SSE",
        "S",
        "SSW",
        "SW",
        "WSW",
        "W",
        "WNW",
        "NW",
        "NNW",
    )

    for i, label in enumerate(labels):
        angle = np.deg2rad(i * 360.0 / len(labels))
        sin_angle = np.sin(angle)
        cos_angle = np.cos(angle)

        mark_arr = np.array(
            (
                (
                    inner_radius * sin_angle,
                    inner_radius * cos_angle,
                    0.0,
                ),
                (
                    outer_radius * sin_angle,
                    outer_radius * cos_angle,
                    0.0,
                ),
            ),
            dtype=np.float32,
        )[:, :dims]

        ax.plot(
            *mark_arr.T,
            color=linecolor,
            linewidth=linewidth,
            zorder=0,
        )

        text_radius = outer_radius + VISUALIZATION_CONFIG.DEFAULT_OFFSET * scale

        text_arr = np.array(
            (
                text_radius * sin_angle,
                text_radius * cos_angle,
                0.0,
            ),
            dtype=np.float32,
        )[:dims]


        if abs(sin_angle) < 1e-6:
            ha = "center"
        elif sin_angle > 0.0:
            ha = "left"
        else:
            ha = "right"

        if abs(cos_angle) < 1e-6:
            va = "center"
        elif cos_angle > 0.0:
            va = "bottom"
        else:
            va = "top"

        ax.text(
            *text_arr,
            label,
            ha=ha,
            va=va,
            fontsize=10 if label == "N" else 8,
            zorder=0,
            clip_on=False,
        )


def plot_sunpath(
    sun_points: Sequence["Point3D"],
    sun_polylines: Sequence["Polyline3D"],
    sun_arcs: Sequence["Arc3D"],
    filtered_data: Union["HourlyContinuousCollection", "HourlyDiscontinuousCollection", None] = None,
    scale: Optional[float] = None,
    projection: Literal["Orthographic", "Stereographic"] = "Orthographic",
    *,
    ax: Optional["Axes"] = None,
    cmap: Optional["LinearSegmentedColormap"] = None,
    linewidth: float = 1,
    linecolor: str = "gray",
) -> Union["Axes", "Axes3D"]:
    scale = 1.0 if scale is None else scale

    cmap = cmap or LADYBUG_CONFIG.DEFAULT_CMAP

    sun_points_arr:"NDArray[np.float32]" = points_vectors_2_array(sun_points).astype(np.float32)*scale # shape (n, 3)
    if sun_points_arr.ndim != 2 or sun_points_arr.shape[1] != 3:
        raise ValueError(
            "sun_points_arr must have shape (n, 3)."
        )

    sun_polylines_pts: List["NDArray[np.float32]"] = []
    for polyline in sun_polylines:
        polyline_points_arr = points_vectors_2_array(
            cast(Tuple["Point3D"], polyline.vertices)
        ).astype(np.float32)*scale # shape (m, 3)

        sun_polylines_pts.append(polyline_points_arr)

    sun_arcs_pts: List["NDArray[np.float32]"] = []
    for arc in sun_arcs:
        arc_points_arr = points_vectors_2_array(
            cast(Tuple["Point3D"], cast("Polyline3D", arc.to_polyline(32)).vertices)
        ).astype(np.float32)*scale # shape (m, 3)

        sun_arcs_pts.append(arc_points_arr)

    data_values = np.asarray(
        cast(Tuple[float], filtered_data.values),
        dtype=np.float32,
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

    sun_points_arr = sun_points_arr[:, :2] if projection == "Orthographic" else sun_points_arr

    if data_values is not None:
        scatter = ax.scatter(
            *sun_points_arr.T,
            s = 2,
            marker="o",
            cmap=cmap,
            c=data_values
        )
        header = cast("Header", cast(
            Union["HourlyContinuousCollection", "HourlyDiscontinuousCollection", "Header"],
            filtered_data
        ).header)
        fig = cast("Figure", ax.get_figure())
        cbar = fig.colorbar(
            scatter,
            ax=ax,
            aspect=25,
        )
        cbar.set_label(
            f"{header.data_type.name} ({header.unit})",
        )

    for pt_arr in sun_polylines_pts:
        pt_arr = pt_arr[:, :2] if projection == "Orthographic" else pt_arr
        ax.plot(
            *pt_arr.T,
            color=linecolor,
            linewidth=linewidth,
            zorder=1,
        )

    for pt_arr in sun_arcs_pts:
        pt_arr = pt_arr[:, :2] if projection == "Orthographic" else pt_arr
        ax.plot(
            *pt_arr.T,
            color=linecolor,
            linewidth=linewidth,
            zorder=1,
        )

    _plot_compass(
        ax,
        projection,
        scale,
        linewidth=linewidth,
        linecolor=linecolor,
    )

    ax.set_aspect("equal", adjustable="box") if projection == "Orthographic" else ax.set_box_aspect((1, 1, 0.5))
    return ax
