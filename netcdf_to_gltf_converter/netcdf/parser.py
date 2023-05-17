from typing import Generator, List

import numpy as np
import xarray as xr
from xugrid import Ugrid2d

from netcdf_to_gltf_converter.config import Config, Variable
from netcdf_to_gltf_converter.data.mesh import MeshAttributes, TriangularMesh
from netcdf_to_gltf_converter.netcdf.wrapper import UgridDataset
from netcdf_to_gltf_converter.preprocessing.interpolation import Interpolator, Location
from netcdf_to_gltf_converter.preprocessing.transformation import Transformer
from netcdf_to_gltf_converter.preprocessing.triangulation import Triangulator
from netcdf_to_gltf_converter.types import Color
from netcdf_to_gltf_converter.utils.arrays import uint32_array

xr.set_options(keep_attrs=True)


class Parser:
    """Class to parse a xr.DataArray into a set of TriangularMeshes."""

    def __init__(self) -> None:
        """Initialize a Parser."""

        self._interpolator = Interpolator()
        self._triangulator = Triangulator()

    def parse(self, dataset: xr.Dataset, config: Config) -> List[TriangularMesh]:
        """Parse the provided data set to a list of TriangularMeshes.

        Args:
            dataset (xr.Dataset): The NetCDF dataset.
            config (Config): The converter configuration.
        """
        ugrid_dataset = UgridDataset(dataset, config)
        tranformer = Transformer(ugrid_dataset, config)
        tranformer.shift()
        tranformer.scale()
        grid = Ugrid2d.from_dataset(dataset, ugrid_dataset.topology_2d)
        triangulated_grid = self._triangulator.triangulate(grid)

        triangular_meshes = []

        for variable in config.variables:
            data_mesh = self.to_triangular_mesh(
                variable, triangulated_grid, ugrid_dataset
            )
            triangular_meshes.append(data_mesh)

            if variable.use_threshold:
                threshold_mesh = data_mesh.get_threshold_mesh(
                    variable.threshold_height * config.scale, variable.threshold_color
                )
                triangular_meshes.append(threshold_mesh)

        return triangular_meshes

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
        color: Color,
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

            yield MeshAttributes(
                vertex_positions=vertex_displacements, mesh_color=color
            )

    def to_triangular_mesh(
        self, variable: Variable, grid: Ugrid2d, ugrid_dataset: UgridDataset
    ):
        data = ugrid_dataset.get_variable(variable.name)
        data_coords = ugrid_dataset.get_data_coordinates(data)
        data_values = data.isel(time=0).to_numpy()

        interpolated_data = self._interpolate(data_coords, data_values, grid)

        base = MeshAttributes(
            vertex_positions=interpolated_data, mesh_color=variable.color
        )
        triangles = uint32_array(grid.face_node_connectivity)
        transformations = list(
            self._get_transformations(data, data_coords, grid, base, variable.color)
        )

        return TriangularMesh(
            base=base,
            triangles=triangles,
            transformations=transformations,
        )
