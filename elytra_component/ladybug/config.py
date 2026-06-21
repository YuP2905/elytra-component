from __future__ import annotations
from typing import (
    Final,
    Tuple,
    TYPE_CHECKING,
)
if TYPE_CHECKING:
    from matplotlib.colors import LinearSegmentedColormap
    from ..ladybug.typing import LadybugColorSetName

from dataclasses import dataclass

from ..ladybug.visualization.config import (
    # LADYBUG_COLORSET_NAMES as _LADYBUG_COLORSET_NAMES,
    # DEFAULT_COLORSET as _DEFAULT_COLORSET,
    VISUALIZATION_CONFIG
)
from ..ladybug.utils import (
    get_ladybug_cmap,
)

#! Here, using ladybug's epw map is a temporary solution
#! until I have my own map(EyuHub/map)
_DEFAULT_EPW_MAP_URL = "https://www.ladybug.tools/epwmap/"


@dataclass(frozen=True, slots=True)
class LadybugConfig:
    DEFAULT_EPW_MAP_URL: Final[str]
    LADYBUG_COLORSET_NAMES: Final[Tuple["LadybugColorSetName", ...]]
    DEFAULT_COLORSET: Final["LadybugColorSetName"]
    DEFAULT_CMAP: Final["LinearSegmentedColormap"]


LADYBUG_CONFIG = LadybugConfig(
    DEFAULT_EPW_MAP_URL = _DEFAULT_EPW_MAP_URL,
    DEFAULT_COLORSET = VISUALIZATION_CONFIG.DEFAULT_COLORSET,
    LADYBUG_COLORSET_NAMES = VISUALIZATION_CONFIG.LADYBUG_COLORSET_NAMES,
    DEFAULT_CMAP = get_ladybug_cmap(VISUALIZATION_CONFIG.DEFAULT_COLORSET),
)
