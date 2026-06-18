from __future__ import annotations
from typing import (
    Tuple,
    Optional,
    cast,
    TYPE_CHECKING,
)

from ladybug.windrose import WindRose
import matplotlib.pyplot as plt

from ._matplotlib import (
    data_collection_title,
    plot_compass,
    plot_colorbar,
    plot_geometry,
    plot_mesh,
    style_ladybug_axes,
)
from ..typing import (
    ColorbarOrientation,
    MatplotlibColor,
)

if TYPE_CHECKING:
    from ladybug_geometry.geometry2d.line import LineSegment2D
    from ladybug_geometry.geometry2d.mesh import Mesh2D
    from ladybug.datacollection import BaseCollection
    from matplotlib.axes import Axes


def plot_wind_rose(
    direction_data: "BaseCollection",
    analysis_data: "BaseCollection",
    direction_count: int = 36,
    *,
    ax: Optional["Axes"] = None,
    show_frequency_lines: bool = True,
    show_orientation_lines: bool = True,
    show_compass_labels: bool = True,
    show_colorbar: bool = True,
    show_title: bool = True,
    colorbar_discrete: bool = True,
    colorbar_orientation: Optional[ColorbarOrientation] = None,
    linecolor: MatplotlibColor = "black",
    linewidth: float = 0.35,
    edgecolor: Optional[MatplotlibColor] = None,
) -> "Axes":
    """Plot a Ladybug wind rose with matplotlib.

    Args:
        direction_data: Ladybug wind direction data collection.
        analysis_data: Ladybug wind speed or analysis data collection.
        direction_count: Number of direction bins.
        ax: Optional matplotlib axes.
        show_frequency_lines: Whether to draw frequency interval outlines.
        show_orientation_lines: Whether to draw orientation lines.
        show_compass_labels: Whether to draw compass ticks and direction labels.
        show_colorbar: Whether to draw a Matplotlib colorbar.
        show_title: Whether to draw Header metadata and frequency information.
        colorbar_discrete: Whether to display discrete color segments.
        colorbar_orientation: Optional Matplotlib colorbar orientation.
        linecolor: Line color.
        linewidth: Line width.
        edgecolor: Optional mesh edge color.

    Returns:
        The matplotlib axes containing the plot.
    """
    wind_rose = WindRose(
        direction_data,
        analysis_data,
        direction_count,
    )

    if ax is None:
        _, ax = plt.subplots()

    plot_mesh(
        ax,
        cast("Mesh2D", wind_rose.colored_mesh),
        edgecolor=edgecolor,
    )

    if show_frequency_lines:
        for polygon in wind_rose.frequency_lines:
            plot_geometry(
                ax,
                polygon,
                color=linecolor,
                linewidth=linewidth,
            )

    if show_orientation_lines:
        for line in wind_rose.orientation_lines:
            plot_geometry(
                ax,
                cast("LineSegment2D", line),
                color=linecolor,
                linewidth=linewidth,
            )

    if show_compass_labels:
        plot_compass(
            ax,
            wind_rose.compass,
            color=linecolor,
            linewidth=linewidth,
        )

    if show_colorbar:
        plot_colorbar(
            ax,
            wind_rose.legend,
            discrete=colorbar_discrete,
            orientation=colorbar_orientation,
        )

    if show_title:
        title = data_collection_title(analysis_data)
        if wind_rose.zero_count is not None:
            calm_percentage = (
                wind_rose.zero_count
                / len(cast("Tuple[float]", wind_rose.analysis_values))
                * 100.0
            )
            title += (
                f"\nCalm for {calm_percentage:.2f}% of the time"
                f" = {wind_rose.zero_count} hours."
            )
        frequency_percentage = (
            wind_rose.frequency_hours
            / len(cast("Tuple[float]", wind_rose.analysis_values))
            * 100.0
        )
        title += (
            "\nEach closed polygon shows frequency of "
            f"{frequency_percentage:.1f}%"
            f" = {wind_rose.frequency_hours:g} hours."
        )
        ax.set_title(
            title,
            loc="left",
            fontsize=8.0,
        )

    style_ladybug_axes(ax)
    return ax
