from enum import Enum
from typing import Tuple
import xugrid as xu
import numpy as np
import xarray as xr

from netcdf_to_gltf_converter.config import Config
from netcdf_to_gltf_converter.netcdf.conventions import (
    AttrKey,
    CfRoleAttrValue,
    LocationAttrValue,
)


class Topology(str, Enum):
    """The topology as described by the ugrid_roles."""

    nodes = "node_coordinates"
    edges = "edge_coordinates"
    faces = "face_coordinates"


class UgridDataset:
    """Class that serves as a wrapper object for an xarray.DataArray with UGrid conventions.
    The wrapper allows for easier retrieval of relevant data.
    """

    def __init__(self, dataset: xr.Dataset, config: Config) -> None:
        """Initialize a UgridDataset with the specified arguments.

        Args:
            dataset (xr.Dataset): The xarray Dataset.
            config (Config): The converter configuration.
        """
        self._dataset = dataset
        self._config = config

        self.topology_2d = self._get_topology_2d()
        self._topologies = dataset.ugrid_roles.coordinates[self.topology_2d]

    @property
    def ugrid2d(self) -> xu.Ugrid2d:
        """Get the xu.Ugrid2d from the data set.

        Returns:
            xu.Ugrid2d: A xu.Ugrid2d created from the data set.
        """
        return xu.Ugrid2d.from_dataset(self._dataset, self.topology_2d)
    
    @property
    def node_coord_vars(self) -> Tuple[xr.DataArray, xr.DataArray]:
        """Get the two node coordinate variables, one for the x-coordinates and one for the y-coordinates.

        Returns:
            Tuple[xr.DataArray, xr.DataArray]: A tuple where the first item is the DataArray containing the node x-coordinates
            and the second item is the DataArray containing the node y-coordinates.
        """
        return self._get_coord_vars_for_topology(Topology.nodes)

    @property
    def edge_coord_vars(self) -> Tuple[xr.DataArray, xr.DataArray]:
        """Get the two edge coordinate variables, one for the x-coordinates and one for the y-coordinates.

        Returns:
            Tuple[xr.DataArray, xr.DataArray]: A tuple where the first item is the DataArray containing the edge x-coordinates
            and the second item is the DataArray containing the edge y-coordinates.
        """
        return self._get_coord_vars_for_topology(Topology.edges)

    @property
    def face_coord_vars(self) -> Tuple[xr.DataArray, xr.DataArray]:
        """Get the two face coordinate variables, one for the x-coordinates and one for the y-coordinates.

        Returns:
            Tuple[xr.DataArray, xr.DataArray]: A tuple where the first item is the DataArray containing the face x-coordinates
            and the second item is the DataArray containing the face y-coordinates.
        """
        return self._get_coord_vars_for_topology(Topology.faces)

    def get_data_coordinates(self, data: xr.DataArray) -> np.ndarray:
        """Get the coordinates for the provided data.

        Args:
            data (xr.DataArray): The data to get the coordinates for.

        Returns:
            np.ndarray: A 2D np.ndarray of floats with shape (n, 2) where each row contains a x and y coordinate.
        """
        location = data.attrs.get(AttrKey.location)
        return self._get_coordinates_for_location(location)

    def set_variable(self, variable: xr.DataArray):
        """Update the variable in the data set.

        Args:
            variable (xr.DataArray): The variable to update.

        Raises:
            ValueError: When the dataset does not contain a variable with the same name.
        """
        if variable.name not in self._dataset:
            raise ValueError(
                f"Cannot update variable '{variable.name}' in dataset: variable does not exist"
            )

        self._dataset[variable.name] = variable

    def get_variable(self, variable_name: str) -> xr.DataArray:
        """Get the variable with the specified name from the data set.

        Args:
            variable_name (str): The variable name.

        Returns:
            xr.DataArray: An xr.DataArray containing the variable data.

        Raises:
            ValueError: When the dataset does not contain a variable with the name.
        """
        if variable_name not in self._dataset:
            raise ValueError(
                f"Cannot get variable '{variable_name}' in dataset: variable does not exist"
            )

        return self._dataset[variable_name]

    def _get_coordinates_for_location(self, location: LocationAttrValue) -> np.ndarray:
        x_coord_var, y_coord_var = self._get_coord_vars_for_location(location)
        x_coords = x_coord_var.values
        y_coords = y_coord_var.values
        coords = np.column_stack([x_coords, y_coords])

        return coords

    def _get_coord_vars_for_location(self, location: LocationAttrValue) -> np.ndarray:
        if location == LocationAttrValue.node:
            return self.node_coord_vars
        if location == LocationAttrValue.edge:
            return self.edge_coord_vars
        if location == LocationAttrValue.face:
            return self.face_coord_vars
        raise ValueError(f"Location {location} not supported.")

    def _get_coord_vars_for_topology(self, location: Topology) -> Tuple:
        var_names = self._topologies[location]
        x_coord_var = self.get_variable(var_names[0][0])
        y_coord_var = self.get_variable(var_names[1][0])

        return x_coord_var, y_coord_var

    def _get_topology_2d(self) -> str:
        attr_filter = {
            AttrKey.cf_role: CfRoleAttrValue.mesh_topology,
            AttrKey.topology_dimension: 2,
        }
        variable = next(self._get_variables_by_attr_filter(**attr_filter))
        return variable.name

    def _get_variables_by_attr_filter(self, **filter):
        dataset = self._dataset.filter_by_attrs(**filter)
        for variable in dataset.values():
            yield variable
