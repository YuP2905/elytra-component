from __future__ import annotations

from typing import (
    Dict,
    Optional,
    Sequence,
    Tuple,
    Union,
    cast,
    TYPE_CHECKING,
)

from ladybug.color import Color
from ladybug.legend import LegendParametersCategorized
from matplotlib.cm import ScalarMappable
from matplotlib.colors import (
    BoundaryNorm,
    LinearSegmentedColormap,
    ListedColormap,
    Normalize,
)
import numpy as np

from ..array import (
    coordinates_to_2d,
    coordinates_to_3d,
    geometry_to_array,
    locations_to_array,
    mesh_face_arrays,
)


if TYPE_CHECKING:
    from ladybug.compass import Compass
    from ladybug.datacollection import BaseCollection
    from ladybug_geometry.geometry2d.line import LineSegment2D
    from ladybug_geometry.geometry2d.mesh import Mesh2D
    from ladybug_geometry.geometry2d.pointvector import Point2D
    from ladybug_geometry.geometry2d.polygon import Polygon2D
    from ladybug_geometry.geometry2d.polyline import Polyline2D
    from ladybug_geometry.geometry3d.line import LineSegment3D
    from ladybug_geometry.geometry3d.mesh import Mesh3D
    from ladybug_geometry.geometry3d.plane import Plane
    from ladybug_geometry.geometry3d.pointvector import Point3D
    from ladybug_geometry.geometry3d.polyline import Polyline3D
    from ladybug.legend import Legend
    from matplotlib.axes import Axes
    from matplotlib.colorbar import Colorbar
    from matplotlib.collections import (
        PathCollection,
        PolyCollection,
    )
    from matplotlib.colors import Colormap
    from matplotlib.figure import Figure
    from mpl_toolkits.mplot3d import Axes3D
    from mpl_toolkits.mplot3d.art3d import (
        Path3DCollection,
        Poly3DCollection,
    )
    from numpy.typing import NDArray
    from ..typing import (
        ColorbarOrientation,
        MatplotlibTickAxis,
        MatplotlibColor,
        MatplotlibTextMethod,
    )


def color_to_mpl(
    color: Union[Color, "MatplotlibColor"],
) -> "MatplotlibColor":
    """Convert a Ladybug color or matplotlib color into matplotlib format."""
    if isinstance(color, Color):
        return color.to_hex()
    return color


def _plot_coordinates(
    coordinates: "NDArray[np.float64]",
    spatial: bool,
) -> "NDArray[np.float64]":
    """Return coordinates prepared for an explicitly selected plot mode."""
    return (
        coordinates_to_3d(coordinates)
        if spatial
        else coordinates_to_2d(coordinates)
    )


def mesh_face_colors(
    mesh: Union["Mesh2D", "Mesh3D"],
    fallback: "MatplotlibColor" = "lightgray",
) -> Tuple[
    Union[
        str,
        Tuple[float, float, float],
        Tuple[float, float, float, float],
    ],
    ...,
]:
    """Return face colors for a Ladybug mesh."""
    colors = mesh.colors
    if not colors:
        return tuple(
            fallback
            for _ in mesh.faces
        )

    if mesh.is_color_by_face:
        return tuple(
            color_to_mpl(cast(Color, color))
            for color in colors
        )

    return tuple(
        color_to_mpl(cast(Color, colors[0]))
        for _ in mesh.faces
    )


def plot_coordinates(
    ax: Union["Axes", "Axes3D"],
    coordinates: "NDArray[np.float64]",
    *,
    spatial: bool = False,
    color: "MatplotlibColor" = "black",
    linewidth: float = 1.0,
) -> None:
    """Plot coordinate rows using an explicitly selected plot mode."""
    coordinate_array = _plot_coordinates(
        coordinates,
        spatial,
    )
    ax.plot(
        *coordinate_array.T,
        color=color_to_mpl(color),
        linewidth=linewidth,
    )


def plot_geometry(
    ax: Union["Axes", "Axes3D"],
    geometry: Union[
        "LineSegment2D",
        "LineSegment3D",
        "Polygon2D",
        "Polyline2D",
        "Polyline3D",
    ],
    *,
    spatial: bool = False,
    color: "MatplotlibColor" = "black",
    linewidth: float = 1.0,
) -> None:
    """Plot Ladybug geometry according to its coordinates and axes."""
    plot_coordinates(
        ax,
        geometry_to_array(geometry),
        spatial=spatial,
        color=color,
        linewidth=linewidth,
    )


def plot_mesh(
    ax: Union["Axes", "Axes3D"],
    mesh: Union["Mesh2D", "Mesh3D"],
    *,
    spatial: bool = False,
    edgecolor: Optional["MatplotlibColor"] = None,
    linewidth: float = 0.0,
) -> Union["PolyCollection", "Poly3DCollection"]:
    """Plot a Ladybug mesh according to its coordinates and axes."""
    face_arrays = tuple(
        _plot_coordinates(
            face_array,
            spatial,
        )
        for face_array in mesh_face_arrays(mesh)
    )
    face_colors = mesh_face_colors(mesh)
    edge_colors = (
        "none"
        if edgecolor is None
        else color_to_mpl(edgecolor)
    )

    if spatial:
        from mpl_toolkits.mplot3d.art3d import Poly3DCollection

        axes_3d = cast("Axes3D", ax)
        has_data = axes_3d.has_data()
        current_x_limits = axes_3d.get_xlim()
        current_y_limits = axes_3d.get_ylim()
        current_z_limits = axes_3d.get_zlim()
        all_vertices = np.concatenate(face_arrays)

        collection_3d = Poly3DCollection(
            face_arrays,
            facecolors=face_colors,
            edgecolors=edge_colors,
            linewidths=linewidth,
        )
        axes_3d.add_collection3d(collection_3d)
        x_values = all_vertices[:, 0]
        y_values = all_vertices[:, 1]
        z_values = all_vertices[:, 2]
        if has_data:
            x_values = np.concatenate(
                (
                    x_values,
                    current_x_limits,
                )
            )
            y_values = np.concatenate(
                (
                    y_values,
                    current_y_limits,
                )
            )
            z_values = np.concatenate(
                (
                    z_values,
                    current_z_limits,
                )
            )
        axes_3d.auto_scale_xyz(
            x_values,
            y_values,
            z_values,
        )
        return collection_3d

    from matplotlib.collections import PolyCollection

    collection = PolyCollection(
        face_arrays,
        facecolors=face_colors,
        edgecolors=edge_colors,
        linewidths=linewidth,
    )
    cast("Axes", ax).add_collection(collection)
    cast("Axes", ax).autoscale_view()
    return collection


def plot_points(
    ax: Union["Axes", "Axes3D"],
    points: "NDArray[np.float64]",
    *,
    spatial: bool = False,
    size: int = 5,
    color: Union[
        MatplotlibColor,
        Sequence[MatplotlibColor],
        "NDArray[np.float64]",
    ] = "black",
    cmap: Optional["Colormap"] = None,
) -> Union["PathCollection", "Path3DCollection"]:
    """Plot point rows according to the dimension of the axes."""
    point_coordinates = _plot_coordinates(
        points,
        spatial,
    )
    return ax.scatter(
        *point_coordinates.T,
        s=size,
        color=color if cmap is None else None,
        c=color if cmap is not None else None,
        cmap=cmap,
    )


def plot_text(
    ax: Union["Axes", "Axes3D"],
    points: Sequence[Union["Point2D", "Point3D", "Plane"]],
    labels: Sequence[str],
    *,
    spatial: bool = False,
    fontsize: float = 8.0,
    color: "MatplotlibColor" = "black",
    horizontal_alignment: str = "left",
    vertical_alignment: str = "baseline",
    rotation: float = 0.0,
) -> None:
    """Plot text according to the point coordinates and axes."""
    point_coordinates = _plot_coordinates(
        locations_to_array(points),
        spatial,
    )
    text_properties: Dict[str, object] = {
        "fontsize": fontsize,
        "color": color_to_mpl(color),
        "ha": horizontal_alignment,
        "va": vertical_alignment,
    }
    if not spatial:
        text_properties["rotation"] = rotation

    text_method = cast(
        "MatplotlibTextMethod",
        ax.text,
    )
    for point, label in zip(
        point_coordinates,
        labels,
    ):
        text_method(
            *point,
            label,
            **text_properties,
        )


def tick_values(
    points: Sequence[Union["Point2D", "Point3D", "Plane"]],
    axis: "MatplotlibTickAxis",
) -> Tuple[float, ...]:
    """Return axis coordinate values from Ladybug label points."""
    coordinates = locations_to_array(points)
    axis_index = 0 if axis == "x" else 1
    return tuple(
        float(value)
        for value in coordinates[:, axis_index]
    )


def set_axis_ticks(
    ax: Union["Axes", "Axes3D"],
    points: Sequence[Union["Point2D", "Point3D", "Plane"]],
    labels: Sequence[str],
    axis: "MatplotlibTickAxis",
    *,
    rotation: float = 0.0,
) -> None:
    """Set Matplotlib-native ticks from Ladybug label points."""
    ticks = tick_values(
        points,
        axis,
    )
    tick_labels = tuple(labels)
    if axis == "x":
        ax.set_xticks(
            ticks,
            labels=tick_labels,
            rotation=rotation,
        )
        return

    ax.set_yticks(
        ticks,
        labels=tick_labels,
        rotation=rotation,
    )


def data_collection_title(
    data: "BaseCollection",
    *,
    include_analysis_period: bool = True,
) -> str:
    """Return a title containing the data type, unit, and Header metadata."""
    header = data.header
    title_lines = [
        f"{header.data_type} ({header.unit})",
    ]
    if include_analysis_period:
        title_lines.append(str(header.analysis_period))
    title_lines.extend(
        f"{key}: {value}"
        for key, value in header.metadata.items()
    )
    return "\n".join(title_lines)


def _colorbar_colormap(
    legend: "Legend",
    discrete: bool,
) -> "Colormap":
    """Return a Matplotlib colormap matching a Ladybug legend."""
    colors = tuple(
        color_to_mpl(cast(Color, color))
        for color in legend.segment_colors
    )
    if discrete:
        return ListedColormap(
            colors,
            name="ladybug_discrete",
        )
    if len(colors) == 1:
        colors = (
            colors[0],
            colors[0],
        )
    return LinearSegmentedColormap.from_list(
        "ladybug_continuous",
        colors,
    )


def plot_colorbar(
    ax: Union["Axes", "Axes3D"],
    legend: "Legend",
    *,
    discrete: bool = True,
    orientation: Optional["ColorbarOrientation"] = None,
) -> "Colorbar":
    """Plot a Matplotlib colorbar using Ladybug legend semantics."""
    legend_parameters = legend.legend_parameters
    colorbar_orientation = orientation or (
        "vertical"
        if legend_parameters.vertical
        else "horizontal"
    )
    color_map = _colorbar_colormap(
        legend,
        discrete,
    )
    labels = tuple(cast(str, label) for label in legend.segment_text)

    if isinstance(
        legend_parameters,
        LegendParametersCategorized,
    ):
        color_count = len(legend.segment_colors)
        boundaries = np.arange(
            color_count + 1,
            dtype=np.float64,
        )
        ticks = np.arange(
            color_count,
            dtype=np.float64,
        ) + 0.5
        norm = BoundaryNorm(
            boundaries,
            color_map.N,
        )
    else:
        ticks = np.asarray(
            legend.segment_numbers,
            dtype=np.float64,
        )
        if (
            legend_parameters.min is None
            or legend_parameters.max is None
        ):
            raise ValueError(
                "Ladybug legend minimum and maximum must be defined."
            )
        minimum = float(cast(Union[float, int], legend_parameters.min))
        maximum = float(cast(Union[float, int], legend_parameters.max))
        if discrete:
            if len(ticks) == 1 or minimum == maximum:
                boundaries = np.asarray(
                    (
                        minimum - 0.5,
                        maximum + 0.5,
                    ),
                    dtype=np.float64,
                )
            else:
                boundaries = np.concatenate(
                    (
                        np.asarray((minimum,), dtype=np.float64),
                        (ticks[:-1] + ticks[1:]) / 2.0,
                        np.asarray((maximum,), dtype=np.float64),
                    )
                )
            norm = BoundaryNorm(
                boundaries,
                color_map.N,
            )
        else:
            norm = Normalize(
                vmin=minimum,
                vmax=maximum,
            )

    scalar_mappable = ScalarMappable(
        norm=norm,
        cmap=color_map,
    )
    scalar_mappable.set_array(
        np.asarray(
            legend.values,
            dtype=np.float64,
        )
    )
    figure = cast(
        "Figure",
        ax.get_figure(),
    )
    colorbar = figure.colorbar(
        scalar_mappable,
        ax=ax,
        orientation=colorbar_orientation,
        ticks=ticks,
    )
    colorbar.set_ticks(
        tuple(float(tick) for tick in ticks),
        labels=labels,
    )
    if legend.title:
        colorbar.set_label(legend.title)
    return colorbar


def plot_compass(
    ax: Union["Axes", "Axes3D"],
    compass: "Compass",
    *,
    spatial: bool = False,
    show_boundary: bool = False,
    color: MatplotlibColor = "black",
    linewidth: float = 0.35,
) -> None:
    """Plot Ladybug compass geometry and direction labels."""
    if show_boundary:
        for circle in compass.all_boundary_circles:
            plot_geometry(
                ax,
                circle.to_polyline(128),
                spatial=spatial,
                color=color,
                linewidth=linewidth,
            )

    for tick in (
        *compass.major_azimuth_ticks,
        *compass.minor_azimuth_ticks,
    ):
        plot_geometry(
            ax,
            tick,
            spatial=spatial,
            color=color,
            linewidth=linewidth,
        )

    plot_text(
        ax,
        compass.major_azimuth_points,
        compass.MAJOR_TEXT,
        spatial=spatial,
        fontsize=9.0,
        horizontal_alignment="center",
        vertical_alignment="center",
    )
    plot_text(
        ax,
        compass.minor_azimuth_points,
        compass.MINOR_TEXT,
        spatial=spatial,
        fontsize=7.0,
        horizontal_alignment="center",
        vertical_alignment="center",
    )


def style_ladybug_axes(
    ax: "Axes",
) -> None:
    """Apply shared matplotlib spacing to a Ladybug chart."""
    ax.set_aspect(
        "equal",
        adjustable="box",
    )
    ax.margins(0.02)
