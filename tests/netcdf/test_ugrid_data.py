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
        
    def test_shift(self):
        grid = Factory.create_rectilinear_grid()
        dataset = UgridDataset(grid.to_dataset())
        
        # All x-coordinates subtracted with 10, and y-coordinates with 5
        exp_node_x = np.array([-10, -9, -8, -10, -9, -8, -10, -9, -8])
        exp_node_y = np.array([-5, -5, -5, -4, -4, -4, -3, -3, -3])
        exp_node_coords = np.column_stack([exp_node_x, exp_node_y])
        exp_face_node_connectivity = dataset.face_node_connectivity.copy()
        
        dataset.shift_coordinates(shift_x=10, shift_y=5, shift_z=0, variables=[])

        assert np.array_equal(dataset.node_coordinates, exp_node_coords)
        assert np.array_equal(dataset.face_node_connectivity, exp_face_node_connectivity)
        
    def test_scale_scales_x_and_y_coordinates(self):
        grid = Factory.create_rectilinear_grid()
        dataset = UgridDataset(grid.to_dataset())
        
        # All x- and y-coordinates multiplied by 2
        exp_node_x = np.array([0, 2, 4, 0, 2, 4, 0, 2, 4])
        exp_node_y = np.array([0, 0, 0, 2, 2, 2, 4, 4, 4])
        exp_node_coords = np.column_stack([exp_node_x, exp_node_y])
        exp_face_node_connectivity = dataset.face_node_connectivity.copy()
        
        dataset.scale_coordinates(scale_horizontal=2, scale_vertical=3, variables=[])

        assert np.array_equal(dataset.node_coordinates, exp_node_coords)
        assert np.array_equal(dataset.face_node_connectivity, exp_face_node_connectivity)
        
    def test_scale_scales_variable_data(self):
        grid = Factory.create_rectilinear_grid()
        dataset = grid.to_dataset()
        
        var_name = "some_var"
        dataset[var_name] = xr.DataArray([1, 2, 3, 4, 5, 6, 7, 8, 9], dims=[f"mesh2d_nNodes"])
        ugrid_dataset = UgridDataset(dataset)
                
        ugrid_dataset.scale_coordinates(scale_horizontal=2, scale_vertical=3, variables=[var_name])
        
        # All data values multiplied by 3
        exp_values = np.array([3, 6, 9, 12, 15, 18, 21, 24, 27])
        
        assert np.array_equal(ugrid_dataset.get_array(var_name).values, exp_values)
