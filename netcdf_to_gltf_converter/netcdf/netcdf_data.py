import logging
from abc import ABC, abstractmethod
from typing import List, Tuple

import numpy as np
from pyproj import CRS
import xarray as xr
import xugrid.ugrid.connectivity as connectivity
from xugrid.ugrid.conventions import X_STANDARD_NAMES, Y_STANDARD_NAMES

from netcdf_to_gltf_converter.data.vector import Vec3


def get_coordinate_variables(data, standard_names: tuple) -> List[xr.DataArray]:
    coord_vars = []
    for coord_var_name in data.coords:
        coord_var = data.coords[coord_var_name]

        coord_standard_name = coord_var.attrs.get("standard_name")
        if coord_standard_name in standard_names:
            coord_vars.append(coord_var)

    return coord_vars


class DataVariable:
    """Class that serves as a wrapper object for an xarray.DataArray.
    The wrapper allows for easier retrieval of relevant data.
    """

    def __init__(self, data: xr.DataArray) -> None:
        """Initialize a DataVariable with the specified data.

        Args:
            data (xr.DataArray): The variable data.
        """
        self._data_array = data
        self._time_var = get_coordinate_variables(data, ("time",))[0]
        self._x_coords_var = get_coordinate_variables(data, X_STANDARD_NAMES)[0]
        self._y_coords_var = get_coordinate_variables(data, Y_STANDARD_NAMES)[0]

    @property
    def x_coords(self) -> np.ndarray:
        """Get the x-coordinates for this data variable.

        Returns:
            np.ndarray: A 1D np.ndarray of floats with shape (n, 1) where each row contains an x-coordinate.
        """
        return self._x_coords_var.values.flatten()
    
    @property
    def y_coords(self) -> np.ndarray:
        """Get the y-coordinates for this data variable.

        Returns:
            np.ndarray: A 1D np.ndarray of floats with shape (n, 1) where each row contains a y-coordinate.
        """
        return self._y_coords_var.values.flatten()
    
    @property
    def coordinates(self) -> np.ndarray:
        """Get the coordinates for this data variable.

        Returns:
            np.ndarray: A 2D np.ndarray of floats with shape (n, 2) where each row contains a x and y coordinate.
        """
        return np.column_stack([self.x_coords, self.y_coords])

    @property
    def time_index_max(self) -> int:
        """Get the maximum time step index for this data variable.

        Returns:
            int: An integer specifying the maximum time step index.
        """
        return self._time_var.size - 1

    def get_data_at_time(self, time_index: int) -> np.ndarray:
        """Get the variable values at the specified time index.

        Args:
            time_index (int): The time index.

        Returns:
            np.ndarray: A 1D np.ndarray of floats.
        """
        time_filter = {self._time_var.name : time_index}
        return self._data_array.isel(**time_filter).values.flatten()

    def get_data_at_coordinate_index(self, coord_index: int) -> np.ndarray:
        """Get the data values for this variable at the specified coordinate index.
        Number of values is equal to the number of time steps.

        Args:
            coord_index (int): The coordinate index.

        Returns:
            np.ndarray: The values at the specified coordinate index.
        """
        filter = self._get_data_on_coordinate_filter(coord_index)
        return self._data_array.isel(filter).values

    def set_data_at_coordinate_index(
        self, coord_index: int, values: np.ndarray
    ) -> None:
        """Set the data values for this variable at the specified coordinate index.
        Number of values should be equal to the number of time steps.

        Args:
            coord_index (int): The coordinate index.
            values (np.ndarray): The new values.
        """
        filter = self._get_data_on_coordinate_filter(coord_index)
        self._data_array.loc[filter] = values

    @property
    def min(self) -> float:
        """Get the minimum value for this variable across all dimensions.
        
        Returns:
            float: The minimum variable value.
        """
        return self._data_array.min().values
    
    @property
    def max(self) -> float:
        """Get the maximum value for this variable across all dimensions.
        
        Returns:
            float: The maximum variable value.
        """
        return self._data_array.max().values

    def _get_data_on_coordinate_filter(self, coord_index: int):
        filter = {self._x_coords_var.dims[0]: coord_index}
        return filter


class DatasetBase(ABC):
    """Class that serves as a wrapper object for an xarray.Dataset.
    The wrapper allows for easier retrieval of relevant data.
    """

    def __init__(self, dataset: xr.Dataset) -> None:
        """Initialize a DatasetBase with the specified arguments.

        Args:
            dataset (xr.Dataset): The xarray Dataset.
        """
        self._dataset = dataset

    @property
    @abstractmethod
    def min_x(self) -> float:
        """Get the smallest x-coordinate of the grid.

        Returns:
            float: A floating value with the smallest x-coordinate.
        """
        pass

    @property
    @abstractmethod
    def min_y(self) -> float:
        """Get the smallest y-coordinate of the grid.

        Returns:
            float: A floating value with the smallest y-coordinate.
        """
        pass

    def set_array(self, array: xr.DataArray):
        """Update the variable in the data set.

        Args:
            variable (xr.DataArray): The variable array to update.

        Raises:
            ValueError: When the dataset does not contain a variable with the same name.
        """
        self._raise_if_not_in_dataset(array.name)
        self._dataset[array.name] = array

    def get_array(self, variable_name: str) -> xr.DataArray:
        """Get the variable array with the specified name from the data set.

        Args:
            variable_name (str): The variable name.

        Returns:
            xr.DataArray: An xr.DataArray containing the variable data.

        Raises:
            ValueError: When the dataset does not contain a variable with the name.
        """
        self._raise_if_not_in_dataset(variable_name)
        return self._dataset[variable_name]

    def get_variable(self, variable_name: str) -> DataVariable:
        """Get the variable with the specified name from the data set.

        Args:
            variable_name (str): The variable name.

        Returns:
            DataVariable: The wrapper object for the variable.

        Raises:
            ValueError: When the dataset does not contain a variable with the name.
        """
        data = self.get_array(variable_name)
        return DataVariable(data)

    def _raise_if_not_in_dataset(self, name: str):
        if name not in self._dataset:
            raise ValueError(f"Variable with name {name} does not exist in dataset.")
    
    @property
    @abstractmethod
    def face_node_connectivity(self) -> np.ndarray:
        """Get the face node connectivity of the grid.

        Returns:
            np.ndarray: An ndarray of floats with shape (n, 3). Each row represents one face and contains the three node indices that define the face.
        """
        pass

    @abstractmethod
    def set_face_node_connectivity(self, face_node_connectivity: np.ndarray):
        """Set the face node connectivity of the grid.

        Args:
            face_node_connectivity (np.ndarray): An ndarray of floats with shape (n, 3). Each row represents one face and contains the three node indices that define the face.
        """
        pass

    @property
    @abstractmethod
    def node_coordinates(self) -> np.ndarray:
        """Get the node coordinates of the grid.

        Returns:
            np.ndarray: An ndarray of floats with shape (n, 2). Each row represents one node and contains the x- and y-coordinate.
        """
        pass

    @property
    @abstractmethod
    def fill_value(self) -> int:
        """Get the fill value.

        Returns:
            int: Integer with the fill value.
        """
        pass
    
    @abstractmethod
    def transform_vertical_coordinate_system(
        self, source_crs: CRS, target_crs: CRS, variables: List[str]
    ) -> None:
        """Transform the vertical coordinates to another coordinate system.

        Args:
            source_crs (CRS): The source coordinate system.
            target_crs (CRS): The target coordinate system.
            variables (List[str]): The names of the variables for which to transform the values.
        """
        pass

    @abstractmethod
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
        pass
    
    @abstractmethod
    def scale_coordinates(self, scale_horizontal: float, scale_vertical: float, variables: List[str]) -> None:
        """
        Scale the x- and y-coordinates and the data values, with the scaling factors that are specified.
        The original data set is updated with the new coordinates.

        Args:
            scale_horizontal (float): The horizontal scale for the x- and y-coordinates of the mesh.
            scale_vertical (float): The vertical scale for the height of the mesh points.
            variables (List[str]): The names of the variables to scale.
        """
        pass
    

    def triangulate(self):
        """Triangulate the provided grid.

        Args:
            dataset (DatasetBase): The grid to triangulate.
        """

        face_node_connectivity, _ = connectivity.triangulate(
            self.face_node_connectivity, self.fill_value
        )
        self.set_face_node_connectivity(face_node_connectivity)
        
    def _log_grid_bounds(self, bounds: Tuple[float, float, float, float]):
        logging.info(f"Grid bounds: {bounds[0]} (min x), {bounds[1]} (min y), {bounds[2]} (max x), {bounds[3]} (max y)")