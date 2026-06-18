from __future__ import annotations
from typing import (
    Optional,
    Tuple,
    Union,
    cast,
    TYPE_CHECKING,
)

from ladybug.hourlyplot import HourlyPlot
import matplotlib.pyplot as plt

from ._matplotlib import (
    plot_geometry,
    plot_colorbar,
    plot_mesh,
    set_axis_ticks,
    style_ladybug_axes,
)
from ..typing import (
    ColorbarOrientation,
    MatplotlibColor,
)

if TYPE_CHECKING:
    from ladybug.datacollection import (
        HourlyContinuousCollection,
        HourlyDiscontinuousCollection,
    )
    from ladybug.legend import LegendParameters
    from matplotlib.axes import Axes
    from mpl_toolkits.mplot3d import Axes3D


def plot_hourly(
    data: "HourlyContinuousCollection | HourlyDiscontinuousCollection",
    legend_parameters: Optional["LegendParameters"] = None,
    z_dim: float = 0.0,
    reverse_y: bool = False,
    clock_24: bool = False,
    *,
    ax: Optional[Union["Axes", "Axes3D"]] = None,
    show_labels: bool = True,
    show_colorbar: bool = True,
    show_title: bool = True,
    show_grid: bool = True,
    colorbar_discrete: bool = True,
    colorbar_orientation: Optional[ColorbarOrientation] = None,
    edgecolor: Optional[MatplotlibColor] = None,
    grid_color: MatplotlibColor = "black",
    grid_linewidth: float = 0.35,
) -> Union["Axes", "Axes3D"]:
    """Plot a Ladybug hourly data collection with matplotlib.

    Args:
        data: Hourly Ladybug data collection to plot.
        legend_parameters: Optional Ladybug legend parameters.
        z_dim: Total Z height used to map data values onto a 3D mesh.
        reverse_y: Whether to reverse the y-axis in the Ladybug chart.
        clock_24: Whether to use 24-hour labels.
        ax: Optional matplotlib axes.
        show_labels: Whether to draw month and hour labels.
        show_colorbar: Whether to draw a Matplotlib colorbar.
        show_title: Whether to draw the data Header title.
        show_grid: Whether to draw month and hour grid lines.
        colorbar_discrete: Whether to display discrete color segments.
        colorbar_orientation: Optional Matplotlib colorbar orientation.
        edgecolor: Optional mesh edge color.
        grid_color: Grid line color.
        grid_linewidth: Grid line width.

    Returns:
        The matplotlib axes containing the plot.
    """
    hourly_plot = HourlyPlot(
        data,
        legend_parameters,
        z_dim=cast(int, z_dim),
        reverse_y=reverse_y,
    )
    spatial = z_dim != 0.0

    if ax is None:
        figure = plt.figure()
        ax = figure.add_subplot(
            111,
            projection="3d" if spatial else None,
        )
        ax = cast(Union["Axes", "Axes3D"], ax)

    plot_mesh(
        ax,
        hourly_plot.colored_mesh3d
        if spatial
        else hourly_plot.colored_mesh2d,
        spatial=spatial,
        edgecolor=edgecolor,
    )
    plot_geometry(
        ax,
        hourly_plot.chart_border3d
        if spatial
        else hourly_plot.chart_border2d,
        spatial=spatial,
        color=grid_color,
        linewidth=grid_linewidth,
    )

    if show_grid:
        month_lines = (
            hourly_plot.month_lines3d
            if spatial
            else hourly_plot.month_lines2d
        )
        for line in month_lines:
            plot_geometry(
                ax,
                line,
                spatial=spatial,
                color=grid_color,
                linewidth=grid_linewidth,
            )
        hour_lines = (
            hourly_plot.hour_lines3d
            if spatial
            else hourly_plot.hour_lines2d
        )
        for line in hour_lines:
            plot_geometry(
                ax,
                line,
                spatial=spatial,
                color=grid_color,
                linewidth=grid_linewidth,
            )

    if show_labels:
        if hourly_plot.month_labels is not None:
            set_axis_ticks(
                ax,
                hourly_plot.month_label_points3d
                if spatial
                else hourly_plot.month_label_points2d,
                hourly_plot.month_labels,
                "x",
            )
        if hourly_plot.hour_labels is not None:
            hour_labels = (
                hourly_plot.hour_labels_24
                if clock_24
                else hourly_plot.hour_labels
            )
            set_axis_ticks(
                ax,
                hourly_plot.hour_label_points3d
                if spatial
                else hourly_plot.hour_label_points2d,
                cast("Tuple[str, ...]", hour_labels),
                "y",
            )

    if show_title:
        ax.set_title(
            hourly_plot.title_text,
            loc="left",
            fontsize=8.0,
        )

    if show_colorbar:
        plot_colorbar(
            ax,
            hourly_plot.legend,
            discrete=colorbar_discrete,
            orientation=colorbar_orientation,
        )

    if not spatial:
        style_ladybug_axes(cast("Axes", ax))
    return ax
