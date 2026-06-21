from __future__ import annotations

from typing import (
    Optional,
    TYPE_CHECKING,
)
if TYPE_CHECKING:
    from os import PathLike
    from ..typing import (
        DetailLevel,
        RecipeType,
    )

from honeybee_radiance_command.options.rfluxmtx import RfluxmtxOptions
from honeybee_radiance_command.options.rpict import RpictOptions
from honeybee_radiance_command.options.rtrace import RtraceOptions
from lbt_recipes.settings import RecipeSettings
from pathlib import Path

from ..utils import option_values
from ..config import (
    DETAIL_LEVELS,
    RADIANCE_OPTION_MAP,
    RECIPE_TYPES,
)


def recipe_settings(
    folder: Optional["PathLike[str]"] = None,
    workers: Optional[int] = None,
    reload_old: bool = False,
    debug_folder: Optional["PathLike[str]"] = None,
) -> RecipeSettings:
    """Create lbt-recipes run settings.

    Args:
        folder: Recipe project folder.
        workers: Number of worker processes.
        reload_old: Reuse a previous recipe run when possible.
        debug_folder: Optional debug folder.

    Returns:
        Recipe settings used by lbt-recipes.
    """
    return RecipeSettings(
        str(Path(folder)) if folder is not None else None,
        workers,
        reload_old,
        False,
        debug_folder=str(Path(debug_folder)) if debug_folder is not None else None,
    )


def radiance_parameter(
    recipe_type: "RecipeType",
    detail_level: "DetailLevel" = "low",
    additional_par: Optional[str] = None,
) -> str:
    """Create a Radiance parameter string for a recipe type.

    Args:
        recipe_type: Radiance command family used by the recipe.
        detail_level: Preset detail level.
        additional_par: Extra Radiance command parameters.

    Returns:
        Radiance command parameter string.
    """
    command_name = RECIPE_TYPES[recipe_type.lower()]
    detail = DETAIL_LEVELS[detail_level.lower()]
    values = option_values(
        RADIANCE_OPTION_MAP[command_name],
        detail,
    )

    if command_name == "rtrace":
        option = RtraceOptions()
    elif command_name == "rpict":
        option = RpictOptions()
    else:
        option = RfluxmtxOptions()

    for option_name, option_value in values.items():
        setattr(
            option,
            option_name,
            option_value,
        )

    if additional_par is not None:
        option.update_from_string(additional_par)

    return option.to_radiance()
