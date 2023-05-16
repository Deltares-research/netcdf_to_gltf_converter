from enum import Enum
from typing import Generator

import numpy as np
import xarray as xr
from xugrid import Ugrid2d

from netcdf_to_gltf_converter.config import Config
from netcdf_to_gltf_converter.data.mesh import MeshAttributes, TriangularMesh
from netcdf_to_gltf_converter.netcdf.conventions import AttrKey, AttrValue
from netcdf_to_gltf_converter.preprocessing.interpolation import Interpolator, Location
from netcdf_to_gltf_converter.preprocessing.triangulation import Triangulator
from netcdf_to_gltf_converter.utils.arrays import uint32_array


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
    water_level = "sea_surface_height"
    """"Sea surface height" is a time-varying quantity."""


class Wrapper:
    def __init__(self, dataset: xr.Dataset, config: Config) -> None:
        """Initialize a Wrapper with the specified arguments.

        Args:
            dataset (xr.Dataset): The NetCDF dataset.
            config (Config): The converter configuration.
        """

        self._dataset = dataset
        self._config = config
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

    def _get_coordinates(self, location: DataLocation) -> np.ndarray:
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
        attr_filter = {
            AttrKey.cf_role: AttrValue.mesh_topology,
            AttrKey.topology_dimension: 2,
        }
        variable = next(self._get_variables_by_attr_filter(**attr_filter))
        return variable.name

    def _get_2d_variable(self, standard_name: str) -> xr.DataArray:
        attr_filter = {
            AttrKey.standard_name: standard_name,
            AttrKey.mesh: self._2d_topology,
        }
        variable = next(self._get_variables_by_attr_filter(**attr_filter))
        return variable

    def _get_transformations(
        self,
        data: xr.DataArray,
        data_coords: np.ndarray,
        grid: Ugrid2d,
        base: MeshAttributes,
    ) -> Generator[MeshAttributes, None, None]:
        n_times = data.sizes["time"]
        for time_index in range(1, n_times):
            data_values = data.isel(time=time_index).to_numpy()
            np.multiply(data_values, self._config.scale, out=data_values)
            interpolated_data = self._interpolate(data_coords, data_values, grid)
            vertex_displacements = np.subtract(
                interpolated_data,
                base.vertex_positions,
                dtype=np.float32,
            )

            yield MeshAttributes(vertex_positions=vertex_displacements)

    def to_triangular_mesh(self, standard_name: str):
        data = self._get_2d_variable(standard_name)
        data_location = data.attrs.get(AttrKey.location)
        data_coords = self._get_coordinates(data_location)
        data_values = data.isel(time=0).to_numpy()

        self._config.shift_coordinates = True
        if self._config.shift_coordinates:
            self._shift_coordinates(data_coords)

        if self._config.scale != 1.0:
            self._scale_coordinates(data_coords, data_values)

        triangulated_grid = self._triangulator.triangulate(self._grid)
        interpolated_data = self._interpolate(
            data_coords, data_values, triangulated_grid
        )

        base = MeshAttributes(vertex_positions=interpolated_data)
        triangles = uint32_array(triangulated_grid.face_node_connectivity)
        transformations = list(
            self._get_transformations(data, data_coords, triangulated_grid, base)
        )

        return TriangularMesh(
            base=base,
            triangles=triangles,
            transformations=transformations,
        )

    def _shift_coordinates(self, coordinates: np.ndarray):
        shift_x = self._grid.node_x.min()
        shift_y = self._grid.node_y.min()

        coordinates[:, 0] -= shift_x
        coordinates[:, 1] -= shift_y

        self._grid.node_x -= shift_x
        self._grid.node_y -= shift_y

    def _scale_coordinates(self, coordinates: np.ndarray, data_values: np.ndarray):
        scale = self._config.scale

        np.multiply(coordinates, scale, out=coordinates)
        np.multiply(data_values, scale, out=data_values)
        np.multiply(self._grid.node_x, scale, out=self._grid.node_x)
        np.multiply(self._grid.node_y, scale, out=self._grid.node_y)
