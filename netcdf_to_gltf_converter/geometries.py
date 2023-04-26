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
        validate_array(vertex_positions, "float32", n_shape=2, n_col=3)
        self.vertex_positions = vertex_positions

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
        validate_array(triangles, "uint32", n_shape=2, n_col=3)
        assert mesh_geometry.vertex_positions.size == mesh_transformations[0].vertex_positions.size
        self.mesh_geometry = mesh_geometry
        self.triangles = triangles
        self.mesh_transformations = mesh_transformations
