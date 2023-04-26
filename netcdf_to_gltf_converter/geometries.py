from typing import List

import numpy as np


def validate_array(array: np.ndarray, dtype: str, n_shape: int, n_col: int):
    assert array.dtype == dtype
    assert len(array.shape) == n_shape
    assert array.shape[1] == n_col


class MeshGeometry:
    def __init__(
        self,
        vertex_positions: np.ndarray,
    ) -> None:
        """_summary_

        Args:
            vertex_positions (np.ndarray (n, 3)): float32
        """
        self.vertex_positions = vertex_positions
        self.validate()

    def validate(self):
        validate_array(self.vertex_positions, "float32", n_shape=2, n_col=3)


class TriangularMesh:
    def __init__(
        self,
        mesh_geometry: MeshGeometry,
        triangles: np.ndarray,
        mesh_transformations: List[MeshGeometry],
    ) -> None:
        """Initialize a TriangularMesh with the given arguments.

        Args:
            mesh_geometry (MeshGeometry): The nodes in the mesh.
            triangles (np.ndarray (m, 3)): uint32The triangles in the mesh each containing the three node indices that define the triangle shape and position.
            mesh_transformations (List[MeshGeometry]): The collection of node transformations.
        """
        self.mesh_geometry = mesh_geometry
        self.triangles = triangles
        self.mesh_transformations = mesh_transformations
        self.validate()

    def validate(self):
        validate_array(self.triangles, "uint32", n_shape=2, n_col=3)
        base_mesh_geometry_node_size = self.mesh_geometry.vertex_positions.size
        for mesh_transformation in self.mesh_transformations:
            assert (
                mesh_transformation.vertex_positions.size
                == base_mesh_geometry_node_size
            )
