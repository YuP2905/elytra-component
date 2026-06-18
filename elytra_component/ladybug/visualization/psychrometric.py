from __future__ import annotations
from typing import (
    Tuple,
    Optional,
    cast,
    TYPE_CHECKING,
)

from ladybug.psychchart import PsychrometricChart
import matplotlib.pyplot as plt

from ._matplotlib import (
    plot_geometry,
    plot_colorbar,
    plot_mesh,
    plot_text,
    set_axis_ticks,
    style_ladybug_axes,
)
from ..array import points_vectors_2_array
from ..typing import (
    ColorbarOrientation,
    MatplotlibColor,
)

if TYPE_CHECKING:
    from ladybug.datacollection import BaseCollection
    from ladybug.legend import LegendParameters
    from ladybug_geometry.geometry2d.pointvector import Point2D
    from ladybug_geometry.geometry2d.line import LineSegment2D
    from ladybug_geometry.geometry2d.mesh import Mesh2D
    from matplotlib.axes import Axes


def plot_psychrometric(
    temperature: "BaseCollection",
    relative_humidity: "BaseCollection",
    average_pressure: float = 101325.0,
    legend_parameters: Optional["LegendParameters"] = None,
    min_temperature: float = -20.0,
    max_temperature: float = 50.0,
    max_humidity_ratio: float = 0.03,
    use_ip: bool = False,
    data: Optional["BaseCollection"] = None,
    show_wet_bulb_lines: bool = False,
    *,
    ax: Optional["Axes"] = None,
    show_labels: bool = True,
    show_rh_lines: bool = True,
    show_data_points: bool = False,
    show_colorbar: bool = True,
    show_title: bool = True,
    colorbar_discrete: bool = True,
    colorbar_orientation: Optional[ColorbarOrientation] = None,
    linecolor: MatplotlibColor = "black",
    linewidth: float = 0.35,
    point_color: MatplotlibColor = "black",
    point_size: float = 2.0,
) -> "Axes":
    """Plot a Ladybug psychrometric chart with matplotlib.

    Args:
        temperature: Dry-bulb temperature data collection.
        relative_humidity: Relative humidity data collection.
        average_pressure: Average air pressure in Pa.
        legend_parameters: Optional Ladybug legend parameters for data mesh.
        min_temperature: Minimum chart temperature.
        max_temperature: Maximum chart temperature.
        max_humidity_ratio: Maximum humidity ratio.
        use_ip: Whether to use IP units.
        data: Optional data collection to color psychrometric bins.
        show_wet_bulb_lines: Whether to use wet-bulb instead of enthalpy lines.
        ax: Optional matplotlib axes.
        show_labels: Whether to draw chart labels.
        show_rh_lines: Whether to draw relative humidity lines.
        show_data_points: Whether to draw psychrometric data points.
        show_colorbar: Whether to draw a Matplotlib colorbar.
        show_title: Whether to draw the chart title.
        colorbar_discrete: Whether to display discrete color segments.
        colorbar_orientation: Optional Matplotlib colorbar orientation.
        linecolor: Chart line color.
        linewidth: Chart line width.
        point_color: Data point color.
        point_size: Data point size.

    Returns:
        The matplotlib axes containing the plot.
    """
    chart = PsychrometricChart(
        temperature,
        relative_humidity,
        cast(int, average_pressure),
        legend_parameters,
        min_temperature=cast(int, min_temperature),
        max_temperature=cast(int, max_temperature),
        max_humidity_ratio=max_humidity_ratio,
        use_ip=use_ip,
    )

    if ax is None:
        _, ax = plt.subplots()

    if data is None:
        plot_mesh(
            ax,
            chart.colored_mesh,
        )
        legend = chart.legend
    else:
        data_mesh, container = chart.data_mesh(
            data,
            legend_parameters,
        )
        plot_mesh(
            ax,
            cast("Mesh2D", data_mesh),
        )
        legend = container.legend

    plot_geometry(
        ax,
        chart.chart_border,
        color=linecolor,
        linewidth=linewidth,
    )
    plot_geometry(
        ax,
        chart.saturation_line,
        color=linecolor,
        linewidth=linewidth,
    )

    for line in chart.temperature_lines:
        plot_geometry(
            ax,
            cast("LineSegment2D", line),
            color=linecolor,
            linewidth=linewidth,
        )
    for line in chart.hr_lines:
        plot_geometry(
            ax,
            cast("LineSegment2D", line),
            color=linecolor,
            linewidth=linewidth,
        )

    if show_rh_lines:
        for line in chart.rh_lines:
            plot_geometry(
                ax,
                cast("LineSegment2D", line),
                color=linecolor,
                linewidth=linewidth,
            )

    if show_wet_bulb_lines:
        if chart.wb_lines is not None:
            for line in chart.wb_lines:
                plot_geometry(
                    ax,
                    cast("LineSegment2D", line),
                    color=linecolor,
                    linewidth=linewidth,
                )

    else:
        if chart.enthalpy_lines is not None:
            for line in chart.enthalpy_lines:
                plot_geometry(
                    ax,
                    cast("LineSegment2D", line),
                    color=linecolor,
                    linewidth=linewidth,
                )

    if show_data_points:
        if chart.data_points:
            point_array = points_vectors_2_array(chart.data_points)
            ax.scatter(
                point_array[:, 0],
                point_array[:, 1],
                s=point_size,
                color=point_color,
            )

    if show_labels:
        set_axis_ticks(
            ax,
            chart.temperature_label_points,
            chart.temperature_labels,
            "x",
        )
        set_axis_ticks(
            ax,
            chart.hr_label_points,
            chart.hr_labels,
            "y",
        )
        plot_text(
            ax,
            cast("Tuple[Point2D, ...]", chart.rh_label_points[:-1]),
            chart.rh_labels[:-1],
            fontsize=7.0,
            horizontal_alignment="right",
            vertical_alignment="top",
        )
        if show_wet_bulb_lines and chart.wb_label_points is not None:
            plot_text(
                ax,
                cast("Tuple[Point2D, ...]", chart.wb_label_points),
                chart.wb_labels,
                horizontal_alignment="right",
                vertical_alignment="top",
            )
        elif chart.enthalpy_label_points is not None:
            plot_text(
                ax,
                cast("Tuple[Point2D, ...]", chart.enthalpy_label_points),
                chart.enthalpy_labels,
                horizontal_alignment="right",
                vertical_alignment="top",
            )
        ax.set_xlabel(
            chart.x_axis_text,
            fontsize=9.0,
        )
        ax.set_ylabel(
            chart.y_axis_text,
            fontsize=9.0,
        )

    if show_title:
        ax.set_title(
            chart.title_text,
            loc="left",
            fontsize=8.0,
        )

    if show_colorbar:
        plot_colorbar(
            ax,
            legend,
            discrete=colorbar_discrete,
            orientation=colorbar_orientation,
        )

    style_ladybug_axes(ax)
    return ax
