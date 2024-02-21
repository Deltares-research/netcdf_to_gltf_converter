from enum import Enum

import numpy as np
import xarray as xr
import xugrid as xu

from netcdf_to_gltf_converter.netcdf.ugrid.conventions import AttrKey, CfRoleAttrValue
from netcdf_to_gltf_converter.netcdf.netcdf_data import (
    DatasetBase,
    GridBase,
    VariableBase,
)


class Topology(str, Enum):
    """The topology as described by the ugrid_roles."""

    nodes = "node_coordinates"
    edges = "edge_coordinates"
    faces = "face_coordinates"


class Ugrid(GridBase):
    """Class that serves as a wrapper object for a xu.Ugrid2d object.
    The wrapper allows for easier retrieval of relevant data.
    """

    def __init__(self, ugrid2d: xu.Ugrid2d) -> None:
        """Initialize a Ugrid with the specified arguments.

        Args:
            ugrid2d (xu.Ugrid2d): The ugrid2d.
        """
        self._ugrid2d = ugrid2d

    @property
    def face_node_connectivity(self) -> np.ndarray:
        """Get the face node connectivity of the grid.

        Returns:
            np.ndarray: An ndarray of floats with shape (n, 3). Each row represents one face and contains the three node indices that define the face.
        """
        return self._ugrid2d.face_node_connectivity

    def set_face_node_connectivity(self, face_node_connectivity: np.ndarray):
        """Set the face node connectivity of the grid.

        Args:
            face_node_connectivity (np.ndarray): An ndarray of floats with shape (n, 3). Each row represents one face and contains the three node indices that define the face.
        """
        self._ugrid2d.face_node_connectivity = face_node_connectivity

    @property
    def node_coordinates(self) -> np.ndarray:
        """Get the node coordinates of the grid.

        Returns:
            np.ndarray: An ndarray of floats with shape (n, 2). Each row represents one node and contains the x- and y-coordinate.
        """
        return self._ugrid2d.node_coordinates

    @property
    def fill_value(self) -> int:
        """Get the fill value.

        Returns:
            int: Integer with the fill value.
        """
        return self._ugrid2d.fill_value


class UgridVariable(VariableBase):
    """Class that serves as a wrapper object for an xarray.DataArray with UGrid conventions.
    The wrapper allows for easier retrieval of relevant data.
    """


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
        self._ugrid_data_set_accesor: xu.UgridDatasetAccessor = self._ugrid_data_set.ugrid
        
        self.topology_2d = self._get_topology_2d()
        self._topologies = dataset.ugrid_roles.coordinates[self.topology_2d]

    def transform_coordinate_system(self, source_crs: int, target_crs: int):
        """Transform the coordinates to another coordinate system.
        Args:
            source_crs (int): EPSG from the source coordinate system.
            target_crs (int): EPSG from the target coordinate system.

        """
        self._ugrid_data_set_accesor.set_crs(epsg=source_crs)
        self._ugrid_data_set_accesor = self._ugrid_data_set_accesor.to_crs(epsg=target_crs)
    
    @property
    def grid(self) -> Ugrid:
        """Get the Ugrid from the data set.

        Returns:
            Ugrid: A Ugrid created from the data set.
        """
        ugrid2d = xu.Ugrid2d.from_dataset(self._dataset, self.topology_2d)
        return Ugrid(ugrid2d)

    @property
    def min_x(self) -> float:
        """Gets the smallest x-coordinate of the grid.

        Returns:
            float: A floating value with the smallest x-coordinate.
        """
        coord_var_name = self._topologies[Topology.nodes][0][0]
        coord_var = self.get_array(coord_var_name)
        return coord_var.values.min()

    @property
    def min_y(self) -> float:
        """Gets the smallest y-coordinate of the grid.

        Returns:
            float: A floating value with the smallest y-coordinate.
        """
        coord_var_name = self._topologies[Topology.nodes][1][0]
        coord_var = self.get_array(coord_var_name)
        return coord_var.values.min()

    def get_variable(self, variable_name: str) -> UgridVariable:
        """Get the variable with the specified name from the data set.

        Args:
            variable_name (str): The variable name.

        Returns:
            UgridVariable: A UgridVariable.

        Raises:
            ValueError: When the dataset does not contain a variable with the name.
        """
        data = self.get_array(variable_name)
        return UgridVariable(data)

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
