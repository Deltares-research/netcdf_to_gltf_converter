from enum import Enum
from typing import List

import numpy as np
import xarray as xr
from xugrid import Ugrid2d

from netcdf_to_gltf_converter.data.mesh import MeshAttributes, TriangularMesh
from netcdf_to_gltf_converter.preprocessing.interpolation import Interpolator, Location
from netcdf_to_gltf_converter.preprocessing.triangulation import Triangulator
from netcdf_to_gltf_converter.utils.arrays import uint32_array


class MeshType(str, Enum):
    """Enum containg the valid mesh types as stored in the "mesh" attribute of a data variable."""

    mesh1d = "mesh1d"
    """1D mesh"""
    mesh2d = "Mesh2d"
    """2D mesh"""


class AttrKey(str, Enum):
    """Enum containing variable attribute keys."""

    cf_role = "cf_role"
    """CF role"""
    topology_dimension = "topology_dimension"
    """Topology dimension"""
    mesh = "mesh"
    """Mesh"""
    standard_name = "standard_name"
    """Standard name"""
    location = "location"
    """Mesh location of the data"""


class AttrValue(str, Enum):
    """Enum containing variable attribute values."""

    mesh_topology = "mesh_topology"
    """Mesh topology"""


class DataLocation(str, Enum):
    face = "face"
    node = "node"
    edge = "edge"


class StandardName(str, Enum):
    """Enum containg the valid variable standard names according to the
    NetCDF Climate and Forecast (CF) Metadata Conventions version 1.8.
    See also: http://cfconventions.org/Data/cf-standard-names/current/build/cf-standard-name-table.html
    """

    water_depth = "sea_floor_depth_below_sea_surface"
    """The vertical distance between the sea surface and the seabed as measured at a given point in space including the variance caused by tides and possibly waves."""


class Wrapper:
    def __init__(self, dataset: xr.Dataset) -> None:
        self._dataset = dataset
        self._2d_topology = self._get_2d_topology()
        self._grid = Ugrid2d.from_dataset(dataset, self._2d_topology)
        self._interpolator = Interpolator()
        self._triangulator = Triangulator()

    def _interpolate(
        self, data_coords: np.ndarray, data_values: np.ndarray, grid: Ugrid2d
    ):
        return self._interpolator.interpolate_nearest(
            data_coords, data_values, grid, Location.nodes
        )

    def _get_coordinates(self, location: DataLocation):
        if location == DataLocation.face:
            return self._grid.face_coordinates
        if location == DataLocation.edge:
            return self._grid.edge_coordinates
        if location == DataLocation.node:
            return self._grid.node_coordinates

        raise ValueError(f"Location {location} not supported.")

    def _get_variables_by_attr_filter(self, **filter):
        dataset = self._dataset.filter_by_attrs(**filter)
        for variable in dataset.values():
            yield variable

    def _get_2d_topology(self) -> str:
        filter = {
            AttrKey.cf_role: AttrValue.mesh_topology,
            AttrKey.topology_dimension: 2,
        }
        variable = next(self._get_variables_by_attr_filter(**filter))
        return variable.name

    def _get_2d_variable(self, standard_name: str) -> xr.DataArray:
        filter = {
            AttrKey.standard_name: standard_name,
            AttrKey.mesh: self._2d_topology,
        }
        variable = next(self._get_variables_by_attr_filter(**filter))
        return variable

    def to_triangular_mesh(self):
        data = self._get_2d_variable(StandardName.water_depth)
        data_location = data.attrs.get(AttrKey.location)
        data_coords = self._get_coordinates(data_location)
        data_values = data.isel(time=0)

        triangulated_grid = self._triangulator.triangulate(self._grid)
        interpolated_data = self._interpolate(data_coords, data_values, triangulated_grid)
        
        base_geometry = MeshAttributes(vertex_positions=interpolated_data)

        transformations: List[MeshAttributes] = []
        n_times = data.sizes["time"]
        for time_index in range(1, n_times):
            data_values = data.isel(time=time_index)
            interpolated_data = self._interpolate(
                data_coords, data_values, triangulated_grid
            )
            vertex_displacements = np.subtract(
                interpolated_data,
                base_geometry.vertex_positions,
                dtype=np.float32,
            )
            transformation = MeshAttributes(vertex_positions=vertex_displacements)
            transformations.append(transformation)

        triangular_mesh = TriangularMesh(
            base=base_geometry,
            triangles=uint32_array(triangulated_grid.face_node_connectivity),
            transformations=transformations,
        )
        return triangular_mesh
