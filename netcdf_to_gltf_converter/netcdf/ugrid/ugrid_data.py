from typing import List

import numpy as np
from pyproj import CRS
import xarray as xr
import xugrid as xu

from netcdf_to_gltf_converter.data.vector import Vec3
from netcdf_to_gltf_converter.netcdf.netcdf_data import DatasetBase
from netcdf_to_gltf_converter.preprocessing.crs import create_crs_transformer


class UgridDataset(DatasetBase):
    """Class that serves as a wrapper object for an xarray.Dataset with UGrid conventions.
    The wrapper allows for easier retrieval of relevant data.
    """

    def __init__(self, dataset: xr.Dataset) -> None:
        """Initialize a UgridDataset with the specified arguments.

        Args:
            dataset (xr.Dataset): The xarray Dataset.
        """
        super().__init__(dataset)
        self._ugrid_data_set = xu.UgridDataset(dataset)  
        self._grid = self._get_ugrid2d()
        self._update()

    @property
    def min_x(self) -> float:
        """Gets the smallest x-coordinate of the grid.

        Returns:
            float: A floating value with the smallest x-coordinate.
        """
        min_x, _, _,_ = self._grid.bounds
        return min_x

    @property
    def min_y(self) -> float:
        """Gets the smallest y-coordinate of the grid.

        Returns:
            float: A floating value with the smallest y-coordinate.
        """
        _, min_y, _,_ = self._grid.bounds
        return min_y

    @property
    def face_node_connectivity(self) -> np.ndarray:
        """Get the face node connectivity of the grid.

        Returns:
            np.ndarray: An ndarray of floats with shape (n, 3). Each row represents one face and contains the three node indices that define the face.
        """
        return self._grid.face_node_connectivity

    def set_face_node_connectivity(self, face_node_connectivity: np.ndarray):
        """Set the face node connectivity of the grid.

        Args:
            face_node_connectivity (np.ndarray): An ndarray of floats with shape (n, 3). Each row represents one face and contains the three node indices that define the face.
        """
        self._grid.face_node_connectivity = face_node_connectivity

    @property
    def node_coordinates(self) -> np.ndarray:
        """Get the node coordinates of the grid.

        Returns:
            np.ndarray: An ndarray of floats with shape (n, 2). Each row represents one node and contains the x- and y-coordinate.
        """
        return self._grid.node_coordinates

    @property
    def fill_value(self) -> int:
        """Get the fill value.

        Returns:
            int: Integer with the fill value.
        """
        return self._grid.fill_value

    def transform_vertical_coordinate_system(self, source_crs: CRS, target_crs: CRS, variables: List[str]) -> None:
        """Transform the vertical coordinates to another coordinate system.

        Args:
            source_crs (CRS): The source coordinate system.
            target_crs (CRS): The target coordinate system.
            variables (List[str]): The names of the variables for which to transform the values.
        """
        transformer = create_crs_transformer(source_crs, target_crs)
        for variable_name in variables:
            variable = self.get_variable(variable_name)
            variable.transform_data_values(transformer)
                
    def shift_coordinates(self, shift: Vec3, variables: List[str]) -> None:
        """
        Shift the x- and y-coordinates and the variable values in the data set with the provided shift values.
        All x-coordinates will be subtracted with `shift.x`.
        All y_coordinates will be subtracted with `shift.y`.
        All z_coordinates (variable values) will be subtracted with `shift.z`.

        Args:
            shift (Vec3): Vector containing the values to shift the coordinates with.
            variables (List[str]): The names of the variables for which to shift the values.
        """
        self._grid.node_x = self._grid.node_x - shift.x
        self._grid.node_y = self._grid.node_y - shift.y
        self._update()
        
        for variable_name in variables:
            self._subtract_variable_values(variable_name, shift.z)
           
    def scale_coordinates(self, scale_horizontal: float, scale_vertical: float, variables: List[str]) -> None:
        """
        Scale the x- and y-coordinates and the data values, with the scaling factors that are specified.
        The original data set is updated with the new coordinates.

        Args:
            scale_horizontal (float): The horizontal scale for the x- and y-coordinates of the mesh.
            scale_vertical (float): The vertical scale for the height of the mesh points.
            variables (List[str]): The names of the variables to scale.
        """     
        self._grid.node_x = self._grid.node_x * scale_horizontal
        self._grid.node_y = self._grid.node_y * scale_horizontal          
        self._update()
        
        for variable_name in variables:
            self._multiply_variable_values(variable_name, scale_vertical)

    def _subtract_variable_values(self, variable_name: str, subtraction: float) -> None:
        variable = self.get_array(variable_name)
        shifted_coords_var = variable - subtraction
        self.set_array(shifted_coords_var)

    def _multiply_variable_values(self, variable_name: str, factor: float):
        variable = self.get_array(variable_name)
        scaled_coords_var = variable * factor
        self.set_array(scaled_coords_var)

    def _get_ugrid2d(self) -> xu.Ugrid2d:
        for grid in self._ugrid_data_set.grids:
            if isinstance(grid, xu.Ugrid2d):
                return grid
        raise ValueError("No 2D grid")
 
    def _update(self):
        self._grid._clear_geometry_properties()
        self._ugrid_data_set: xu.UgridDataset = self._ugrid_data_set.ugrid.assign_node_coords().ugrid.assign_face_coords().ugrid.assign_edge_coords()
        self._dataset = self._ugrid_data_set.obj
        
        super()._log_grid_bounds(self._grid.bounds)