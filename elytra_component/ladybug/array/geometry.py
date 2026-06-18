from __future__ import annotations

from typing import (
    List,
    Sequence,
    Tuple,
    Union,
    cast,
    TYPE_CHECKING,
)

from ladybug_geometry.geometry2d.pointvector import Point2D, Vector2D
from ladybug_geometry.geometry3d.plane import Plane
from ladybug_geometry.geometry3d.pointvector import Point3D, Vector3D
import numpy as np

if TYPE_CHECKING:
    from ladybug_geometry.geometry2d.line import LineSegment2D
    from ladybug_geometry.geometry2d.mesh import Mesh2D
    from ladybug_geometry.geometry2d.polygon import Polygon2D
    from ladybug_geometry.geometry2d.polyline import Polyline2D
    from ladybug_geometry.geometry3d.line import LineSegment3D
    from ladybug_geometry.geometry3d.mesh import Mesh3D
    from ladybug_geometry.geometry3d.polyline import Polyline3D
    from numpy.typing import NDArray

    from ..typing import LadybugPointVector


def points_vectors_2_array(
    points_vectors: Union[
        Sequence["LadybugPointVector"],
        "LadybugPointVector",
    ],
) -> "NDArray[np.float64]":
    """Convert Ladybug points or vectors to a float64 coordinate array."""
    if isinstance(
        points_vectors,
        (
            Point2D,
            Vector2D,
            Point3D,
            Vector3D,
        ),
    ):
        point_vector_values: Sequence["LadybugPointVector"] = (points_vectors,)
    else:
        point_vector_values = points_vectors

    return np.asarray(
        [
            pt_vec.to_array()
            for pt_vec in point_vector_values
        ],
        dtype=np.float64,
    )


def locations_to_array(
    locations: Sequence[Union[Point2D, Point3D, Plane]],
) -> "NDArray[np.float64]":
    """Convert Ladybug points or plane origins to a coordinate array."""
    points: List[Union[Point2D, Point3D]] = []
    for loc in locations:
        points.append(
            loc.o
            if isinstance(loc, Plane)
            else loc
        )

    return points_vectors_2_array(points)


def mesh_face_arrays(
    mesh: Union["Mesh2D", "Mesh3D"],
) -> Tuple["NDArray[np.float64]", ...]:
    """Convert every Ladybug mesh face to a coordinate array."""
    return tuple(
        points_vectors_2_array(
            cast(
                Tuple[Union[Point2D, Point3D], ...],
                f_vert,
            )
        )
        for f_vert in mesh.face_vertices
    )


def geometry_to_array(
    geometry: Union[
        "LineSegment2D",
        "LineSegment3D",
        "Polygon2D",
        "Polyline2D",
        "Polyline3D",
    ],
) -> "NDArray[np.float64]":
    """Convert an ordered Ladybug line geometry to one coordinate array."""
    segments = cast(
        Sequence[Union["LineSegment2D", "LineSegment3D", "Polyline2D", "Polyline3D"]],
        geometry.segments
    )
    return points_vectors_2_array(
        (
            cast(Union[Point2D, Point3D], segments[0].p1),
            *cast(
                Tuple[Union[Point2D, Point3D], ...],
                tuple(
                    cast(Union[Point2D, Point3D], segment.p2)
                    for segment in segments
                )
            ),
        )
    )


def coordinates_to_2d(
    coordinates: "NDArray[np.float64]",
) -> "NDArray[np.float64]":
    """Return XY coordinates from a 2D or 3D coordinate array."""
    if coordinates.ndim != 2 or coordinates.shape[1] not in (2, 3):
        raise ValueError(
            "Coordinates must have shape (n, 2) or (n, 3)."
        )
    return np.take(
        coordinates,
        (
            0,
            1,
        ),
        axis=1,
    )


def coordinates_to_3d(
    coordinates: "NDArray[np.float64]",
    z: float = 0.0,
) -> "NDArray[np.float64]":
    """Return XYZ coordinates, embedding 2D coordinates at a Z value."""
    if coordinates.ndim != 2 or coordinates.shape[1] not in (2, 3):
        raise ValueError(
            "Coordinates must have shape (n, 2) or (n, 3)."
        )
    if coordinates.shape[1] == 3:
        return coordinates
    return np.column_stack(
        (
            coordinates,
            np.full(
                coordinates.shape[0],
                z,
                dtype=np.float64,
            ),
        )
    )
