from enum import Enum
from typing import Tuple

import numpy as np
import xarray as xr
from xugrid import Ugrid2d

from netcdf_to_gltf_converter.config import Config
from netcdf_to_gltf_converter.netcdf.conventions import AttrKey, CfRoleAttrValue, LocationAttrValue


class Topology(str, Enum):
    nodes = "node_coordinates"
    edges = "edge_coordinates"
    faces = "face_coordinates"
    
class Wrapper:
    def __init__(self, dataset: xr.Dataset, config: Config) -> None:
        self._dataset = dataset
        self._config = config

        self._topology_2d = self._get_topology_2d()
        self.grid = Ugrid2d.from_dataset(dataset, self._topology_2d)
        self._topologies = dataset.ugrid_roles.coordinates[self._topology_2d]
        
        self._coord_vars = {
            LocationAttrValue.node: self._get_coord_vars(Topology.nodes),
            LocationAttrValue.edge: self._get_coord_vars(Topology.edges),
            LocationAttrValue.face: self._get_coord_vars(Topology.faces)
        }

    def _get_coord_vars(self, location: str) -> Tuple:
        var_names = self._topologies[location]
        x_coord_var = self._dataset[var_names[0][0]]
        y_coord_var = self._dataset[var_names[1][0]]
        
        return x_coord_var, y_coord_var
    
    def _get_coordinates(self, location: str) -> np.ndarray:
        var_names = self._dataset.coords[location]
        
        x_coords = self._dataset[var_names[0]].values
        y_coords = self._dataset[var_names[1]].values
        coords = np.column_stack([x_coords, y_coords])
        
        return coords
    
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

    def _get_coordinates(self, location: LocationAttrValue) -> np.ndarray:
        x_coord_var, y_coord_var = self._coord_vars[location]
        x_coords = x_coord_var.values
        y_coords = y_coord_var.values
        coords = np.column_stack([x_coords, y_coords])
        
        return coords

    def get_2d_variable(self, standard_name: str) -> xr.DataArray:
        attr_filter = {
            AttrKey.standard_name: standard_name,
            AttrKey.mesh: self._topology_2d,
        }
        variable = next(self._get_variables_by_attr_filter(**attr_filter))
        return variable

    def get_data_coordinates(self, data: xr.DataArray):
        data_location = data.attrs.get(AttrKey.location)
        return self._get_coordinates(data_location)
