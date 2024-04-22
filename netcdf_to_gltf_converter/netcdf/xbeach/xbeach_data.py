from typing import List, Tuple

import numpy as np
from pyproj import CRS
import xarray as xr
from xugrid.ugrid.conventions import X_STANDARD_NAMES, Y_STANDARD_NAMES

from netcdf_to_gltf_converter.data.vector import Vec3
from netcdf_to_gltf_converter.netcdf.netcdf_data import (
    DatasetBase, get_coordinate_variables)
from netcdf_to_gltf_converter.preprocessing import connectivity

xr.set_options(keep_attrs=True)
"""Attributes need to be preserved when creating a new DataArray with a transformation."""

class RegularGrid():
    """Represents a grid from an XBEACH output file. 
    XBEACH uses regular grids.
    """
    
    def __init__(self, dataset: xr.Dataset):
        """Initialize a new instance of the `RegularGrid` class.

        Args:
            dataset (xr.Dataset): The dataset retrieved from the netCDF file.
        """
        x_coord_var = get_coordinate_variables(dataset, X_STANDARD_NAMES)[0]
        y_coord_var = get_coordinate_variables(dataset, Y_STANDARD_NAMES)[0]
        n_vertex_cols = len(x_coord_var.data[0])
        n_vertex_rows = len(x_coord_var.data)
        
        self.node_x = x_coord_var.values.flatten()
        self.node_y = y_coord_var.values.flatten()
        self.face_node_connectivity = connectivity.face_node_connectivity_from_regular(n_vertex_rows, n_vertex_cols)

    @property
    def node_coordinates(self) -> np.ndarray:
        """Get the node coordinates of the grid.

        Returns:
            np.ndarray: An ndarray of floats with shape (n, 2). Each row represents one node and contains the x- and y-coordinate.
        """
        return np.column_stack([self.node_x, self.node_y])
    
    @property
    def bounds(self) -> Tuple[float, float, float, float]:
        """Get the grid bounds.

        Returns:
            Tuple[float, float, float, float]: Tuple with min x, min y, max x, max y.
        """
        return (self.node_x.min(), self.node_y.min(), self.node_x.max(), self.node_y.max())

class XBeachDataset(DatasetBase):
    """Class that serves as a wrapper object for an xarray.Dataset with UGrid conventions.
    The wrapper allows for easier retrieval of relevant data.
    """

    def __init__(self, dataset: xr.Dataset) -> None:
        """Initialize a UgridDataset with the specified arguments.

        Args:
            dataset (xr.Dataset): The xarray Dataset.
        """
        dataset = dataset.fillna(0) # TODO check what to do with nan values.
        self._dataset = dataset
        self._grid = RegularGrid(dataset)
        self._log_grid_bounds(self._grid.bounds)
        
    @property
    def min_x(self) -> float:
        """Gets the smallest x-coordinate of the grid.

        Returns:
            float: A floating value with the smallest x-coordinate.
        """
        return self._grid.node_x.min()

    @property
    def min_y(self) -> float:
        """Gets the smallest y-coordinate of the grid.

        Returns:
            float: A floating value with the smallest y-coordinate.
        """
        return self._grid.node_y.min()

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
        return -1

    def transform_vertical_coordinate_system(self, source_crs: CRS, target_crs: CRS, variables: List[str]):
        """Transform the vertical coordinates to another coordinate system.

        Args:
            source_crs (CRS): The source coordinate system.
            target_crs (CRS): The target coordinate system.
            variables (List[str]): The names of the variables for which to transform the values.
        """
        raise NotImplementedError()

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

        for x_coord_var in self._x_coord_vars:
            self._shift(x_coord_var, shift.x)

        for y_coord_var in self._y_coord_vars:
            self._shift(y_coord_var, shift.y)

        for variable in variables:
                self._shift(self.get_array(variable), shift.z)

        self._update()

    def _update(self):
        self._grid = RegularGrid(self._dataset)
        self._log_grid_bounds(self._grid.bounds)
        
    def _shift(self, variable: xr.DataArray, shift: float):
        shifted_coords_var = variable - shift
        self.set_array(shifted_coords_var)
    
    @property
    def _x_coord_vars(self):  
        return get_coordinate_variables(self._dataset, X_STANDARD_NAMES)  
    
    @property
    def _y_coord_vars(self):  
        return get_coordinate_variables(self._dataset, Y_STANDARD_NAMES)  
     
    def scale_coordinates(self, scale_horizontal: float, scale_vertical: float, variables: List[str]) -> None:
        """
        Scale the x- and y-coordinates and the data values, with the scaling factors that are specified.
        The original data set is updated with the new coordinates.

        Args:
            scale_horizontal (float): The horizontal scale for the x- and y-coordinates of the mesh.
            scale_vertical (float): The vertical scale for the height of the mesh points.
            variables (List[str]): The names of the variables to scale.
        """
        
        if scale_horizontal != 1.0:
            for x_coord_var in self._x_coord_vars:
                self._scale(x_coord_var, scale_horizontal)

            for y_coord_var in self._y_coord_vars:
                self._scale(y_coord_var, scale_horizontal)

        if scale_vertical != 1.0:
            for variable in variables:
                self._scale(self.get_array(variable), scale_vertical)
            
        self._update()
        
    def _scale(self, variable: xr.DataArray, scale: float):
        scaled_coords_var = variable * scale
        self.set_array(scaled_coords_var)