from __future__ import annotations
from typing import (
    Final,
    Tuple,
    TYPE_CHECKING,
)
if TYPE_CHECKING:
    from ..ladybug.typing import LadybugColorSetName

from dataclasses import dataclass

from ..ladybug.visualization.config import (
    # LADYBUG_COLORSET_NAMES as _LADYBUG_COLORSET_NAMES,
    # DEFAULT_COLORSET as _DEFAULT_COLORSET,
    VISUALIZATION_CONFIG
)
from ..ladybug.utils import (
    get_ladybug_color_hexes,
)

#! Here, using ladybug's epw map is a temporary solution
#! until I have my own map(EyuHub/map)
_DEFAULT_EPW_MAP_URL = "https://www.ladybug.tools/epwmap/"


@dataclass(frozen=True, slots=True)
class LadybugConfig:
    DEFAULT_EPW_MAP_URL: Final[str]
    LADYBUG_COLORSET_NAMES: Final[Tuple["LadybugColorSetName", ...]]
    DEFAULT_COLORSET: Final["LadybugColorSetName"]
    DEFAULT_COLOR_HEXES: Final[Tuple[str, ...]]


LADYBUG_CONFIG = LadybugConfig(
    DEFAULT_EPW_MAP_URL = _DEFAULT_EPW_MAP_URL,
    DEFAULT_COLORSET = VISUALIZATION_CONFIG.DEFAULT_COLORSET,
    LADYBUG_COLORSET_NAMES = VISUALIZATION_CONFIG.LADYBUG_COLORSET_NAMES,
    DEFAULT_COLOR_HEXES = get_ladybug_color_hexes(VISUALIZATION_CONFIG.DEFAULT_COLORSET),
)
