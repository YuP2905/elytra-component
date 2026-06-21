from __future__ import annotations
from typing import (
    Final,
    Tuple,
    cast,
    get_args,
)
from dataclasses import dataclass
from ...ladybug.typing import (
    LadybugColorSetName
)

DEFAULT_COLORSET_INDEX = 0
LADYBUG_COLORSET_NAMES = cast(
    Tuple[LadybugColorSetName, ...],
    get_args(LadybugColorSetName.__value__)
)
DEFAULT_COLORSET = LADYBUG_COLORSET_NAMES[DEFAULT_COLORSET_INDEX]

@dataclass(frozen=True, slots=True)
class VisualizationConfig:
    DEFAULT_COLORSET_INDEX: Final[int]
    LADYBUG_COLORSET_NAMES: Final[Tuple[LadybugColorSetName, ...]]
    DEFAULT_COLORSET: Final[LadybugColorSetName]

VISUALIZATION_CONFIG = VisualizationConfig(
    DEFAULT_COLORSET_INDEX = DEFAULT_COLORSET_INDEX,
    LADYBUG_COLORSET_NAMES = LADYBUG_COLORSET_NAMES,
    DEFAULT_COLORSET = DEFAULT_COLORSET
)
