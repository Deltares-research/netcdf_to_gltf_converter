import numpy as np

from netcdf_to_gltf_converter.preprocessing.triangulation import Triangulator
from tests.preprocessing.utils import Factory


class TestTriangulator:
    def test_triangulate(self):
        triangulator = Triangulator()
        rectilinear_grid = Factory.create_rectilinear_ugrid2d()
        triangulated_grid = triangulator.triangulate(rectilinear_grid)

        assert np.array_equal(rectilinear_grid.node_x, triangulated_grid.node_x)
        assert np.array_equal(rectilinear_grid.node_y, triangulated_grid.node_y)

        exp_face_node_connectivity = np.array(
            [
                [0, 1, 4],
                [0, 4, 3],
                [1, 2, 5],
                [1, 5, 4],
                [3, 4, 7],
                [3, 7, 6],
                [4, 5, 8],
                [4, 8, 7],
            ]
        )

        assert np.array_equal(
            triangulated_grid.face_node_connectivity, exp_face_node_connectivity
        )
