from enum import Enum
from typing import List

import numpy as np
import xarray as xr
from xugrid import Ugrid2d, UgridDataset

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


class AttrValue(str, Enum):
    """Enum containing variable attribute values."""

    mesh_topology = "mesh_topology"
    """Mesh topology"""


class StandardName(str, Enum):
    """Enum containg the valid variable standard names according to the
    NetCDF Climate and Forecast (CF) Metadata Conventions version 1.8.
    See also: http://cfconventions.org/Data/cf-standard-names/current/build/cf-standard-name-table.html
    """

    water_depth = "sea_floor_depth_below_sea_surface"
    """The vertical distance between the sea surface and the seabed as measured at a given point in space including the variance caused by tides and possibly waves."""
    x_coordinates = "projection_x_coordinate"
    """"x" indicates a vector component along the grid x-axis, when this is not true longitude, positive with increasing x. Projection coordinates are distances in the x- and y-directions on a plane onto which the surface of the Earth has been projected according to a map projection. The relationship between the projection coordinates and latitude and longitude is described by the grid_mapping."""
    y_coordinates = "projection_y_coordinate"
    """"y" indicates a vector component along the grid y-axis, when this is not true latitude, positive with increasing y. Projection coordinates are distances in the x- and y-directions on a plane onto which the surface of the Earth has been projected according to a map projection. The relationship between the projection coordinates and latitude and longitude is described by the grid_mapping."""


class Wrapper:
    @staticmethod
    def data_for_time(variable: xr.DataArray, time_index: int):
        return variable.isel(time=time_index)

    @staticmethod
    def interpolate(data_coords: np.ndarray, data_values: np.ndarray, grid):
        return Interpolator.interpolate_nearest(
            data_coords, data_values, grid, Location.nodes
        )

    def __init__(self, dataset: xr.Dataset) -> None:
        self._dataset = dataset
        self._grid = Ugrid2d.from_dataset(dataset, MeshType.mesh2d)

    def _get_face_coordinates(self):
        face_x = self._grid.face_x
        face_y = self._grid.face_y
        return np.array([face_x, face_y]).T

    def _get_2d_topology(self) -> str:
        for variable_name in self._dataset.data_vars:
            attr = self._dataset[variable_name].attrs
            if (
                attr.get(AttrKey.cf_role) == AttrValue.mesh_topology
                and attr.get(AttrKey.topology_dimension) == 2
            ):
                return variable_name

        raise ValueError("Dataset does not contain 2D topology")

    def _get_variables_by_attr_filter(self, **filter):
        dataset = self._dataset.filter_by_attrs(**filter)
        for variable in dataset.values():
            yield variable

    def _get_2d_variable(self, standard_name: str) -> xr.DataArray:
        standard_name_filter = {
            AttrKey.standard_name: standard_name,
            AttrKey.mesh: self._get_2d_topology(),
        }
        variable = next(self._get_variables_by_attr_filter(**standard_name_filter))
        return variable

    def to_triangular_mesh(self):
        face_coords = self._get_face_coordinates()
        water_depth_data = self._get_2d_variable(StandardName.water_depth)
        data_values = Wrapper.data_for_time(water_depth_data, time_index=0)

        triangulated_grid = Triangulator.triangulate(self._grid)
        interpolated_vertex_positions = Wrapper.interpolate(
            face_coords, data_values, triangulated_grid
        )
        base_geometry = MeshAttributes(vertex_positions=interpolated_vertex_positions)

        transformations: List[MeshAttributes] = []
        n_times = water_depth_data.sizes["time"]
        for time_index in range(1, n_times):
            data_values = Wrapper.data_for_time(water_depth_data, time_index)
            interpolated_vertex_positions = Wrapper.interpolate(
                face_coords, data_values, triangulated_grid
            )
            vertex_displacements = np.subtract(
                interpolated_vertex_positions,
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
