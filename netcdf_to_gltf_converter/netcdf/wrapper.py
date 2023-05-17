from enum import Enum
from typing import Tuple

import numpy as np
import xarray as xr

from netcdf_to_gltf_converter.config import Config
from netcdf_to_gltf_converter.netcdf.conventions import (
    AttrKey,
    CfRoleAttrValue,
    LocationAttrValue,
)


class Topology(str, Enum):
    nodes = "node_coordinates"
    edges = "edge_coordinates"
    faces = "face_coordinates"


class UgridDataset:
    def __init__(self, dataset: xr.Dataset, config: Config) -> None:
        self._dataset = dataset
        self._config = config

        self.topology_2d = self._get_topology_2d()
        self._topologies = dataset.ugrid_roles.coordinates[self.topology_2d]

    @property
    def node_coord_vars(self) -> Tuple[xr.DataArray, xr.DataArray]:
        return self._get_coord_vars_for_topology(Topology.nodes)

    @property
    def edge_coord_vars(self):
        return self._get_coord_vars_for_topology(Topology.edges)

    @property
    def face_coord_vars(self):
        return self._get_coord_vars_for_topology(Topology.faces)

    def get_2d_variable(self, standard_name: str) -> xr.DataArray:
        attr_filter = {
            AttrKey.standard_name: standard_name,
            AttrKey.mesh: self.topology_2d,
        }
        variable = next(self._get_variables_by_attr_filter(**attr_filter))
        return variable

    def get_data_coordinates(self, data: xr.DataArray):
        location = data.attrs.get(AttrKey.location)
        return self._get_coordinates_for_location(location)

    def update(self, data: xr.DataArray):
        self._dataset[data.name] = data

    def _get_coordinates_for_location(self, location: LocationAttrValue) -> np.ndarray:
        x_coord_var, y_coord_var = self._get_coord_vars_for_location(location)
        x_coords = x_coord_var.values
        y_coords = y_coord_var.values
        coords = np.column_stack([x_coords, y_coords])

        return coords

    def _get_coord_vars_for_location(self, location: LocationAttrValue) -> np.ndarray:
        if location == LocationAttrValue.node:
            return self._get_coord_vars_for_topology(Topology.nodes)
        if location == LocationAttrValue.edge:
            return self._get_coord_vars_for_topology(Topology.edges)
        if location == LocationAttrValue.face:
            return self._get_coord_vars_for_topology(Topology.faces)
        raise ValueError(f"Location {location} not supported.")

    def _get_coord_vars_for_topology(self, location: Topology) -> Tuple:
        var_names = self._topologies[location]
        x_coord_var = self._dataset[var_names[0][0]]
        y_coord_var = self._dataset[var_names[1][0]]

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
