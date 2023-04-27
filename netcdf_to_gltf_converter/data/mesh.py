from typing import List

import numpy as np

from netcdf_to_gltf_converter.utils import validate_2d_array
from netcdf_to_gltf_converter.data.colors import DEFAULT_MESH_COLOR

class MeshGeometry:
    def __init__(self, vertex_positions: np.ndarray) -> None:
        """Initialize a MeshGeometry with the specified arguments.

        Args:
            vertex_positions (np.ndarray): The vertex positions, an ndarray of floats with shape (n, 3). Each row represents one vertex and contains the x, y and z coordinate of this vertex.
            vertex_colors (np.ndarray): The vertex colors, an ndarray of floats with shape (n, 4). Each row represents a color defined by its normalized red, green, blue and alpha values.
        Raises:
            AssertionError: When the shape or dtype of the arrays do not match the requirements.
        """
        self.vertex_positions = vertex_positions
        self.vertex_colors = np.array(
            len(vertex_positions) * [DEFAULT_MESH_COLOR], dtype="float32"
        )

        self.validate()

    def validate(self):
        validate_2d_array(self.vertex_positions, "float32", n_col=3)
        validate_2d_array(self.vertex_colors, "float32", n_col=4)


class TriangularMesh:
    def __init__(
        self,
        mesh_geometry: MeshGeometry,
        triangles: np.ndarray,
        mesh_transformations: List[MeshGeometry],
    ) -> None:
        """Initialize a TriangularMesh with the specified arguments.

        Args:
            mesh_geometry (MeshGeometry): The base mesh geometry.
            triangles (np.ndarray): The vertex indices per triangle, an ndarray of integers with shape (m, 3). Each row represents one triangle and contains the three vertex indices of this triangle.
            mesh_transformations (List[MeshGeometry]): The mesh transformations containing the vertex displacements.

        Raises:
            AssertionError: When the shape or dtype of the `triangles` does not match the requirements.
            AssertionError: When the size of the vertex positions in any of the mesh transformations do not match the amount in the base mesh geometry.
        """

        self.mesh_geometry = mesh_geometry
        self.triangles = triangles
        self.mesh_transformations = mesh_transformations
        self.validate()

    def validate(self):
        validate_2d_array(self.triangles, "uint32", n_col=3)

        base_vertex_size = self.mesh_geometry.vertex_positions.size
        for mesh_transformation in self.mesh_transformations:
            assert mesh_transformation.vertex_positions.size == base_vertex_size
