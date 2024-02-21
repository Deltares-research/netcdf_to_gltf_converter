import numpy as np
from tests.preprocessing.utils import Factory


class TestUgridDataset:
    def test_triangulate(self):
        grid = Factory.create_rectilinear_grid()
        exp_node_coords = grid.node_coordinates.copy()
    
        grid.triangulate()
    
        assert np.array_equal(grid.node_coordinates, exp_node_coords)
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
        assert np.array_equal(grid.face_node_connectivity, exp_face_node_connectivity)