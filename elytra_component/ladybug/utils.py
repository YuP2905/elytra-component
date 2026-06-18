from __future__ import annotations
from typing import (
    Tuple,
    cast,
    get_args,
)

from ladybug.color import Colorset
from matplotlib.colors import LinearSegmentedColormap

from .typing import LadybugColorSetName

def get_ladybug_cmap(
    colorset_name: "LadybugColorSetName",
) -> LinearSegmentedColormap:

    colorset_names = cast(
        Tuple[LadybugColorSetName, ...],
        get_args(LadybugColorSetName.__value__),
    )
    cs_index = colorset_names.index(colorset_name)
    cs = Colorset()[cs_index]
    hex_colors = [
        c.to_hex()
        for c in cs
    ]
    return LinearSegmentedColormap.from_list(
        colorset_name,
        hex_colors,
    )
