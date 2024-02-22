import numpy as np
import xarray as xr
from netcdf_to_gltf_converter.netcdf.ugrid.ugrid_data import UgridDataset
from tests.preprocessing.utils import Factory


class TestUgridDataset:
    def test_triangulate(self):
        grid = Factory.create_rectilinear_grid()
        dataset = UgridDataset(grid.to_dataset())
        
        exp_node_coords = dataset.node_coordinates.copy()
    
        dataset.triangulate()
    
        assert np.array_equal(dataset.node_coordinates, exp_node_coords)
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
        assert np.array_equal(dataset.face_node_connectivity, exp_face_node_connectivity)
