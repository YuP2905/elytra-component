from __future__ import annotations
from typing import (
    List,
    Optional,
    Sequence,
    cast,
    TYPE_CHECKING,
)

from ladybug.monthlychart import MonthlyChart
import matplotlib.pyplot as plt

from ._matplotlib import (
    color_to_mpl,
    plot_geometry,
    plot_colorbar,
    plot_mesh,
    set_axis_ticks,
    style_ladybug_axes,
    tick_values,
)
from ..typing import (
    ColorbarOrientation,
    MatplotlibColor,
)

if TYPE_CHECKING:
    from ladybug_geometry.geometry2d.mesh import Mesh2D
    from ladybug_geometry.geometry2d.polyline import Polyline2D
    from ladybug.legend import LegendParameters
    from matplotlib.axes import Axes

    from ..typing import LadybugDataCollection


def plot_monthly(
    data: Sequence["LadybugDataCollection"],
    legend_parameters: Optional["LegendParameters"] = None,
    stack: bool = False,
    percentile: float = 34.0,
    *,
    ax: Optional["Axes"] = None,
    show_labels: bool = True,
    show_colorbar: bool = True,
    show_title: bool = True,
    show_grid: bool = True,
    colorbar_discrete: bool = True,
    colorbar_orientation: Optional[ColorbarOrientation] = None,
    edgecolor: Optional[MatplotlibColor] = None,
    grid_color: MatplotlibColor = "black",
    grid_linewidth: float = 0.35,
) -> "Axes":
    """Plot monthly Ladybug data collections with matplotlib.

    Args:
        data: Monthly-compatible Ladybug data collections.
        legend_parameters: Optional Ladybug legend parameters.
        stack: Whether to stack data collections.
        percentile: Percentile used by Ladybug's MonthlyChart.
        ax: Optional matplotlib axes.
        show_labels: Whether to draw axis labels.
        show_colorbar: Whether to draw a Matplotlib colorbar.
        show_title: Whether to draw Header metadata and Y-axis titles.
        show_grid: Whether to draw grid lines.
        colorbar_discrete: Whether to display discrete color segments.
        colorbar_orientation: Optional Matplotlib colorbar orientation.
        edgecolor: Optional mesh edge color.
        grid_color: Grid line color.
        grid_linewidth: Grid line width.

    Returns:
        The matplotlib axes containing the plot.
    """
    chart = MonthlyChart(
        data,
        legend_parameters,
        stack=stack,
        percentile=cast(int, percentile),
    )

    if ax is None:
        _, ax = plt.subplots()

    if chart.data_meshes is not None:
        for mesh in chart.data_meshes:
            plot_mesh(
                ax,
                cast("Mesh2D", mesh),
                edgecolor=edgecolor,
            )

    line_results = chart.data_polylines_with_colors
    if line_results is not None:
        polylines, colors = line_results
        for polyline, color in zip(
            polylines,
            colors,
        ):
            plot_geometry(
                ax,
                cast("Polyline2D", polyline),
                color=color_to_mpl(color),
                linewidth=max(grid_linewidth, 1.0),
            )
    elif chart.data_polylines is not None:
        for polyline in chart.data_polylines:
            plot_geometry(
                ax,
                cast("Polyline2D", polyline),
                color=grid_color,
                linewidth=max(grid_linewidth, 1.0),
            )

    plot_geometry(
        ax,
        cast("Polyline2D", chart.chart_border),
        color=grid_color,
        linewidth=grid_linewidth,
    )

    if show_grid:
        for line in chart.month_lines:
            plot_geometry(
                ax,
                line,
                color=grid_color,
                linewidth=grid_linewidth,
            )
        for line in chart.y_axis_lines:
            plot_geometry(
                ax,
                line,
                color=grid_color,
                linewidth=grid_linewidth,
            )

    secondary_axis = (
        ax.secondary_yaxis("right")
        if (
            chart.y_axis_label_points2 is not None
            or chart.y_axis_title_text2 is not None
        )
        else None
    )

    if show_labels:
        if chart.month_labels is not None:
            set_axis_ticks(
                ax,
                chart.month_label_points,
                chart.month_labels,
                "x",
            )
        if chart.y_axis_labels1 is not None:
            set_axis_ticks(
                ax,
                chart.y_axis_label_points1,
                cast("List[str]", chart.y_axis_labels1),
                "y",
            )
        if (
            chart.y_axis_label_points2 is not None
            and chart.y_axis_labels2 is not None
        ):
            if secondary_axis is not None:
                secondary_axis.set_yticks(
                    tick_values(
                        chart.y_axis_label_points2,
                        "y",
                    ),
                    labels=tuple(cast("List[str]", chart.y_axis_labels2)),
                )

    if show_title:
        ax.set_title(
            chart.title_text,
            loc="left",
            fontsize=8.0,
        )
        ax.set_ylabel(
            chart.y_axis_title_text1,
            fontsize=9.0,
        )
        if (
            chart.y_axis_title_text2 is not None
            and secondary_axis is not None
        ):
            secondary_axis.set_ylabel(
                chart.y_axis_title_text2,
                fontsize=9.0,
            )

    if show_colorbar:
        plot_colorbar(
            ax,
            chart.legend,
            discrete=colorbar_discrete,
            orientation=colorbar_orientation,
        )

    style_ladybug_axes(ax)
    return ax
