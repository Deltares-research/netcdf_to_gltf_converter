from typing import Generator

import numpy as np
import xarray as xr
from xugrid import Ugrid2d

from netcdf_to_gltf_converter.config import Config
from netcdf_to_gltf_converter.data.mesh import MeshAttributes, TriangularMesh
from netcdf_to_gltf_converter.netcdf.wrapper import UgridDataset
from netcdf_to_gltf_converter.preprocessing.interpolation import Interpolator, Location
from netcdf_to_gltf_converter.preprocessing.transformation import Transformer
from netcdf_to_gltf_converter.preprocessing.triangulation import Triangulator
from netcdf_to_gltf_converter.utils.arrays import uint32_array

xr.set_options(keep_attrs=True)


class Parser:
    def __init__(self, dataset: xr.Dataset, config: Config) -> None:
        """Initialize a Parser with the specified arguments.

        Args:
            dataset (xr.Dataset): The NetCDF dataset.
            config (Config): The converter configuration.
        """

        self._interpolator = Interpolator()
        self._triangulator = Triangulator()
        self._ugrid_dataset = UgridDataset(dataset, config)
        self._tranformer = Transformer(self._ugrid_dataset, config)
        self._tranformer.shift()
        self._tranformer.scale()
        self._grid = Ugrid2d.from_dataset(dataset, self._ugrid_dataset.topology_2d)
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
            interpolated_data = self._interpolate(data_coords, data_values, grid)
            vertex_displacements = np.subtract(
                interpolated_data,
                base.vertex_positions,
                dtype=np.float32,
            )

            yield MeshAttributes(vertex_positions=vertex_displacements)

    def to_triangular_mesh(self, standard_name: str):
        data = self._ugrid_dataset.get_2d_variable(standard_name)
        data_coords = self._ugrid_dataset.get_data_coordinates(data)
        data_values = data.isel(time=0).to_numpy()

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
