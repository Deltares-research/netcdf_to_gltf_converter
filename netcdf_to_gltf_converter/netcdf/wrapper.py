from enum import Enum
import xarray as xr
from netcdf_to_gltf_converter.config import Config
import numpy as np
from xugrid import Ugrid2d

from netcdf_to_gltf_converter.netcdf.conventions import AttrKey, AttrValue
class DataLocation(str, Enum):
    face = "face"
    node = "node"
    edge = "edge"
    
class Wrapper:
    def __init__(self, dataset: xr.Dataset, config: Config) -> None:
        self._dataset = dataset
        self._config = config
        
        self._topology_2d = self._get_topology_2d()
        self.grid = Ugrid2d.from_dataset(dataset, self._topology_2d)
    
    def _get_topology_2d(self) -> str:
        attr_filter = {
            AttrKey.cf_role: AttrValue.mesh_topology,
            AttrKey.topology_dimension: 2,
        }
        variable = next(self._get_variables_by_attr_filter(**attr_filter))
        return variable.name
    
    def _get_variables_by_attr_filter(self, **filter):
        dataset = self._dataset.filter_by_attrs(**filter)
        for variable in dataset.values():
            yield variable

    def _get_coordinates(self, location: DataLocation) -> np.ndarray:
        if location == DataLocation.face:
            return self.grid.face_coordinates
        if location == DataLocation.edge:
            return self.grid.edge_coordinates
        if location == DataLocation.node:
            return self.grid.node_coordinates

        raise ValueError(f"Location {location} not supported.")
    
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
