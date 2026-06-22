from __future__ import annotations
from typing import (
    Tuple,
    cast,
    get_args,
)

from ladybug.color import Colorset

from .typing import LadybugColorSetName

def get_ladybug_color_hexes(
    colorset_name: LadybugColorSetName,
) -> Tuple[str, ...]:
    """Return hex colors from a Ladybug color set.

    Args:
        colorset_name: Ladybug color set name.

    Returns:
        Hex colors ordered by the Ladybug color set.
    """

    colorset_names = cast(
        Tuple[LadybugColorSetName, ...],
        get_args(LadybugColorSetName.__value__),
    )
    cs_index = colorset_names.index(colorset_name)
    cs = Colorset()[cs_index]
    hex_colors = tuple(
        c.to_hex()
        for c in cs
    )
    return hex_colors
