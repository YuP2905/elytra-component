from __future__ import annotations
from typing import (
    List,
    Optional,
    Sequence,
    Tuple,
    cast,
    TYPE_CHECKING,
)
import os

from numba import get_num_threads, njit, prange, set_num_threads
import numpy as np

from ..array import points_vectors_2_array

if TYPE_CHECKING:
    from ladybug_geometry.geometry3d.mesh import Mesh3D
    from ladybug_geometry.geometry3d.pointvector import Point3D, Vector3D
    from numpy.typing import NDArray


@njit(parallel=True, cache=True)
def _analyze_sun_hours(
    points_arr: "NDArray[np.float64]",
    normals_arr: "NDArray[np.float64]",
    rev_vectors_arr: "NDArray[np.float64]",
    triangles_arr: "NDArray[np.float64]",
    geo_block: bool,
    eps: float,
) -> "NDArray[np.uint8]":
    """Calculate visible sun vectors for each point with triangle blockers."""
    n_points = points_arr.shape[0]
    n_vectors = rev_vectors_arr.shape[0]
    n_triangles = triangles_arr.shape[0]

    int_matrix = np.ones(
        (n_points, n_vectors),
        dtype=np.uint8,
    )

    for k in prange(n_points * n_vectors):
        point_i = k // n_vectors
        vector_i = k - point_i * n_vectors

        px = points_arr[point_i, 0]
        py = points_arr[point_i, 1]
        pz = points_arr[point_i, 2]

        nx = normals_arr[point_i, 0]
        ny = normals_arr[point_i, 1]
        nz = normals_arr[point_i, 2]

        dx = rev_vectors_arr[vector_i, 0]
        dy = rev_vectors_arr[vector_i, 1]
        dz = rev_vectors_arr[vector_i, 2]

        if geo_block:
            dot_value = nx * dx + ny * dy + nz * dz

            if dot_value <= 0.0:
                int_matrix[point_i, vector_i] = 0
                continue

        for tri_i in range(n_triangles):
            v0x = triangles_arr[tri_i, 0, 0]
            v0y = triangles_arr[tri_i, 0, 1]
            v0z = triangles_arr[tri_i, 0, 2]

            v1x = triangles_arr[tri_i, 1, 0]
            v1y = triangles_arr[tri_i, 1, 1]
            v1z = triangles_arr[tri_i, 1, 2]

            v2x = triangles_arr[tri_i, 2, 0]
            v2y = triangles_arr[tri_i, 2, 1]
            v2z = triangles_arr[tri_i, 2, 2]

            edge_1_x = v1x - v0x
            edge_1_y = v1y - v0y
            edge_1_z = v1z - v0z

            edge_2_x = v2x - v0x
            edge_2_y = v2y - v0y
            edge_2_z = v2z - v0z

            p_vec_x = dy * edge_2_z - dz * edge_2_y
            p_vec_y = dz * edge_2_x - dx * edge_2_z
            p_vec_z = dx * edge_2_y - dy * edge_2_x

            det = (
                edge_1_x * p_vec_x
                + edge_1_y * p_vec_y
                + edge_1_z * p_vec_z
            )

            if -eps < det < eps:
                continue

            inv_det = 1.0 / det

            t_vec_x = px - v0x
            t_vec_y = py - v0y
            t_vec_z = pz - v0z

            u = inv_det * (
                t_vec_x * p_vec_x
                + t_vec_y * p_vec_y
                + t_vec_z * p_vec_z
            )

            if u < 0.0 or u > 1.0:
                continue

            q_vec_x = t_vec_y * edge_1_z - t_vec_z * edge_1_y
            q_vec_y = t_vec_z * edge_1_x - t_vec_x * edge_1_z
            q_vec_z = t_vec_x * edge_1_y - t_vec_y * edge_1_x

            v = inv_det * (
                dx * q_vec_x
                + dy * q_vec_y
                + dz * q_vec_z
            )

            if v < 0.0 or u + v > 1.0:
                continue

            ray_t = inv_det * (
                edge_2_x * q_vec_x
                + edge_2_y * q_vec_y
                + edge_2_z * q_vec_z
            )

            if ray_t > eps:
                int_matrix[point_i, vector_i] = 0
                break

    return int_matrix


def analyze_sun_hours(
    vectors: Tuple["Vector3D", ...],
    geometry: "Mesh3D",
    context: Optional[Sequence["Mesh3D"]] = None,
    timestep: int = 1,
    offset_dist: Optional[float] = None,
    geo_block: bool = True,
    cpu_count: Optional[int] = None,
) -> Tuple[
    Tuple["Point3D", ...],
    "NDArray[np.float32]",
    "NDArray[np.uint8]",
]:
    """Analyze direct sun hours on a Ladybug Mesh3D.

    Args:
        vectors: Sun vectors from Ladybug sun objects.
        geometry: Study mesh. Face centroids become analysis points.
        context: Optional context meshes that block rays.
        timestep: Number of timesteps per hour.
        offset_dist: Point offset distance along mesh face normals.
        geo_block: Whether the study geometry also blocks rays.
        cpu_count: Optional numba worker count.

    Returns:
        A tuple containing:
        - points: Offset analysis points.
        - results: Sun-hour result for each point.
        - int_matrix: Visibility matrix with shape ``(point_count, vector_count)``.
    """
    timestep = 1 if timestep is None else timestep
    if timestep < 1:
        raise ValueError(
            "The timestep must be a positive integer."
        )

    if offset_dist is None:
        offset_dist = 0.1 if geo_block else 0.0

    workers = (
        cpu_count
        if cpu_count is not None
        else max(1, (os.cpu_count() or 1) - 1)
    )
    if workers < 1:
        raise ValueError(
            "The cpu_count must be a positive integer."
        )

    workers = min(
        workers,
        get_num_threads(),
    )
    set_num_threads(workers)

    context_meshes = tuple() if context is None else tuple(context)

    geom_face_centroids = cast(Tuple["Point3D", ...], geometry.face_centroids)
    geom_face_normals = cast(Tuple["Vector3D", ...], geometry.face_normals)
    points = tuple(
        point.move(vector * offset_dist)
        for point, vector in zip(
            geom_face_centroids,
            geom_face_normals,
        )
    )
    rev_vectors = tuple(
        vector.reverse()
        for vector in vectors
    )

    points_arr = points_vectors_2_array(points)
    geom_face_normals_arr = points_vectors_2_array(geom_face_normals)
    rev_vectors_arr = points_vectors_2_array(rev_vectors)

    shade_meshes = (geometry, *context_meshes) if geo_block else context_meshes

    triangles: List[
        Tuple[
            Tuple[float, float, float],
            Tuple[float, float, float],
            Tuple[float, float, float],
        ]
    ] = []
    for mesh in shade_meshes:
        for face_vertices in mesh.face_vertices:
            vertices = cast(Tuple["Point3D", ...], face_vertices)

            if len(vertices) < 3:
                continue

            p0 = vertices[0]
            for i in range(1, len(vertices) - 1):
                p1 = vertices[i]
                p2 = vertices[i + 1]

                triangles.append(
                    (
                        (p0.x, p0.y, p0.z),
                        (p1.x, p1.y, p1.z),
                        (p2.x, p2.y, p2.z),
                    )
                )

    triangles_arr = (
        np.zeros(
            (0, 3, 3),
            dtype=np.float64,
        )
        if len(triangles) == 0
        else np.asarray(
            triangles,
            dtype=np.float64,
        )
    )

    int_matrix = _analyze_sun_hours(
        points_arr,
        geom_face_normals_arr,
        rev_vectors_arr,
        triangles_arr,
        geo_block,
        1.0e-9,
    )

    results = int_matrix.sum(
        axis=1,
        dtype=np.float32,
    )
    if timestep > 1:
        results = results / np.float32(timestep)

    return points, results, int_matrix
