import numpy as np

from netcdf_to_gltf_converter.netcdf.importer import Importer
from tests.utils import resources


class TestImporter:
    def test_import_from(self):
        file_path = resources / "3x3nodes_rectilinear.nc"
        triangular_grid = Importer.import_from(file_path)

        exp_triangles = np.array(
            [
                [5, 2, 0],
                [5, 0, 1],
                [1, 0, 3],
                [1, 3, 6],
                [2, 7, 4],
                [2, 4, 0],
                [0, 4, 8],
                [0, 8, 3],
            ],
            dtype=np.uint32,
        )

        exp_vertex_positions = np.array(
            [
                [1.0, 1.0, 3.0],
                [0.0, 1.0, 3.0],
                [1.0, 0.0, 3.0],
                [1.0, 2.0, 1.0],
                [2.0, 1.0, 3.0],
                [0.0, 0.0, 3.0],
                [0.0, 2.0, 1.0],
                [2.0, 0.0, 3.0],
                [2.0, 2.0, 1.0],
            ],
            dtype=np.float32,
        )

        exp_vertex_transformations = np.array(
            [
                [
                    [0.0, 0.0, -2.0],
                    [0.0, 0.0, -2.0],
                    [0.0, 0.0, 2.0],
                    [0.0, 0.0, -2.0],
                    [0.0, 0.0, -2.0],
                    [0.0, 0.0, 2.0],
                    [0.0, 0.0, -2.0],
                    [0.0, 0.0, -2.0],
                    [0.0, 0.0, 2.0],
                ],
            ],
            dtype=np.float32,
        )

        np.array_equal(triangular_grid.triangles, exp_triangles)
        np.array_equal(
            triangular_grid.mesh_geometry.vertex_positions, exp_vertex_positions
        )
        assert len(triangular_grid.mesh_transformations) == 1
        np.array_equal(
            triangular_grid.mesh_transformations[0], exp_vertex_transformations
        )
