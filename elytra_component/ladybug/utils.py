from __future__ import annotations
from typing import (

    Union,
    Sequence,
    TYPE_CHECKING,
)
if TYPE_CHECKING:
    from numpy.typing import NDArray
    from ..ladybug.typing import LadybugColorSetName

from ladybug.color import Colorset
from ladybug_geometry.geometry3d.pointvector import Vector3D, Point3D
from matplotlib.colors import LinearSegmentedColormap

import numpy as np

from ..ladybug.visualization.config import VISUALIZATION_CONFIG

def get_ladybug_cmap(
    colorset_name: "LadybugColorSetName",
) -> LinearSegmentedColormap:

    cs_index = VISUALIZATION_CONFIG.LADYBUG_COLORSET_NAMES.index(colorset_name)
    cs = Colorset()[cs_index]
    hex_colors = [
        c.to_hex()
        for c in cs
    ]
    return LinearSegmentedColormap.from_list(
        colorset_name,
        hex_colors,
    )

def points_vectors_2_array(
    points_vectors: Union[Sequence["Point3D"], Sequence["Vector3D"], "Point3D", "Vector3D"],
) -> "NDArray[np.float64]":
    if isinstance(points_vectors, (Point3D, Vector3D)):
        points_vectors = (points_vectors,)
    return np.asarray(
        [
            pv.to_array()
            for pv in points_vectors
        ],
        dtype=np.float64,
    )