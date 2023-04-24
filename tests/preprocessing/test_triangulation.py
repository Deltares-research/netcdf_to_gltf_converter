import numpy as np
import xugrid as xu
from xugrid import Ugrid2d

from netcdf_to_gltf_converter.preprocessing.triangulation import Triangulator

def create_rectilinear_ugrid2d() -> xu.Ugrid2d:
    """
    5--6--7
    |  |  |
    3--4--5
    |  |  |
    0--1--2

    """ 
    node_x = np.array([0,1,2,0,1,2,0,1,2])
    node_y = np.array([0,0,0,1,1,1,2,2,2])
    fill_value= -1
    face_node_connectivity = np.array([
        [0, 1, 4, 3],
        [1, 2, 5, 4],
        [3, 4, 7, 6],
        [4, 5, 8, 7]
    ])

    return xu.Ugrid2d(node_x, node_y, fill_value, face_node_connectivity)
        
        
class TestTriangulator:
    def test_triangulate(self):
        rectilinear_grid = create_rectilinear_ugrid2d()
        triangulated_grid = Triangulator.triangulate(rectilinear_grid)
        
        assert np.array_equal(rectilinear_grid.node_x, triangulated_grid.node_x)
        assert np.array_equal(rectilinear_grid.node_y, triangulated_grid.node_y)
        
        exp_face_node_connectivity = np.array(
            [
                [0,1,4],
                [0,4,3],
                [1,2,5],
                [1,5,4],
                [3,4,7],
                [3,7,6],
                [4,5,8],
                [4,8,7],
            ]
        )
        
        assert np.array_equal(triangulated_grid.face_node_connectivity, exp_face_node_connectivity)
        
        
    
