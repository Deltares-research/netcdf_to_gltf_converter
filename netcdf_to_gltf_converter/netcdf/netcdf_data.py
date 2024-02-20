from abc import ABC, abstractmethod
from typing import List

import numpy as np
import xarray as xr


def get_coordinate_variables(data, standard_name: str) -> List[xr.DataArray]:
    coord_vars = []
    for coord_var_name in data.coords:
        coord_var = data.coords[coord_var_name]

        coord_standard_name = coord_var.attrs.get("standard_name")
        if coord_standard_name == standard_name:
            coord_vars.append(coord_var)

    return coord_vars


class GridBase(ABC):
    """Class that serves as a wrapper object for a grid object.
    The wrapper allows for easier retrieval of relevant data.
    """

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


class VariableBase(ABC):
    """Class that serves as a wrapper object for an xarray.DataArray.
    The wrapper allows for easier retrieval of relevant data.
    """

    def __init__(self, data: xr.DataArray) -> None:
        """Initialize a VariableBase with the specified data.

        Args:
            data (xr.DataArray): The variable data.
        """
        self._data = data
        self._coordinates = self._get_coordinates()
        self._time_var_name = get_coordinate_variables(data, "time")[0].name

    @property
    def coordinates(self) -> np.ndarray:
        """Get the coordinates for this data variable.

        Returns:
            np.ndarray: A 2D np.ndarray of floats with shape (n, 2) where each row contains a x and y coordinate.
        """
        return self._coordinates

    @property
    def time_index_max(self) -> int:
        """Get the maximum time step index for this data variable.

        Returns:
            int: An integer specifying the maximum time step index.
        """
        return self._data.sizes[self._time_var_name] - 1

    def get_data_at_time(self, time_index: int) -> np.ndarray:
        """Get the variable values at the specified time index.

        Args:
            time_index (int): The time index.

        Returns:
            np.ndarray: A 1D np.ndarray of floats.
        """
        time_filter = {self._time_var_name : time_index}
        return self._data.isel(**time_filter).values.flatten()


    def _get_coordinates(self) -> np.ndarray:
        def get_coordinates(standard_name: str):
            return get_coordinate_variables(self._data, standard_name)[0].values.flatten()

        x_coords = get_coordinates("projection_x_coordinate")
        y_coords = get_coordinates("projection_y_coordinate")
        return np.column_stack([x_coords, y_coords])


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
    def grid(self) -> GridBase:
        """Get the grid definition from the data set.

        Returns:
            GridBase: A GridBase object created from the data set.
        """
        pass

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

    @property
    def x_coord_vars(self) -> List[xr.DataArray]:
        """Get the x-coordinate variables.

        Returns:
            List[xr.DataArray]: A list containing the x-coordinate variables.
        """
        return get_coordinate_variables(self._dataset, "projection_x_coordinate")

    @property
    def y_coord_vars(self) -> List[xr.DataArray]:
        """Get the y-coordinate variables.

        Returns:
            List[xr.DataArray]: A list containing the y-coordinate variables.
        """
        return get_coordinate_variables(self._dataset, "projection_y_coordinate")

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

    @abstractmethod
    def get_variable(self, variable_name: str) -> VariableBase:
        """Get the variable with the specified name from the data set.

        Args:
            variable_name (str): The variable name.

        Returns:
            VariableBase: The wrapper object for the variable.

        Raises:
            ValueError: When the dataset does not contain a variable with the name.
        """
        pass

    def _raise_if_not_in_dataset(self, name: str):
        if name not in self._dataset:
            raise ValueError(f"Variable with name {name} does not exist in dataset.")
