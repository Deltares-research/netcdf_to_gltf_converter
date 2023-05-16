from typing import Generator

import numpy as np
import xarray as xr
from xugrid import Ugrid2d

from netcdf_to_gltf_converter.config import Config
from netcdf_to_gltf_converter.data.mesh import MeshAttributes, TriangularMesh
from netcdf_to_gltf_converter.netcdf.wrapper import Wrapper
from netcdf_to_gltf_converter.preprocessing.interpolation import Interpolator, Location
from netcdf_to_gltf_converter.preprocessing.transformation import Transformer
from netcdf_to_gltf_converter.preprocessing.triangulation import Triangulator
from netcdf_to_gltf_converter.utils.arrays import uint32_array


class Parser:
    def __init__(self, dataset: xr.Dataset, config: Config) -> None:
        """Initialize a Wrapper with the specified arguments.

        Args:
            dataset (xr.Dataset): The NetCDF dataset.
            config (Config): The converter configuration.
        """

        self._interpolator = Interpolator()
        self._triangulator = Triangulator()
        self._tranformer = Transformer(dataset, config)
        self._wrapper = Wrapper(dataset, config)
        self._grid = Ugrid2d.from_dataset(dataset, self._wrapper.topology_2d)
        self._dataset = dataset
        self._config = config

    def _interpolate(
        self, data_coords: np.ndarray, data_values: np.ndarray, grid: Ugrid2d
    ):
        return self._interpolator.interpolate_nearest(
            data_coords, data_values, grid, Location.nodes
        )

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
        data = self._wrapper.get_2d_variable(standard_name)
        data_coords = self._wrapper.get_data_coordinates(data)
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
