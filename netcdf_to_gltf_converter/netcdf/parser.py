from typing import Generator, List

import numpy as np
import xarray as xr
from xugrid import Ugrid2d

from netcdf_to_gltf_converter.config import Config, Variable
from netcdf_to_gltf_converter.custom_types import Color
from netcdf_to_gltf_converter.data.mesh import MeshAttributes, TriangularMesh
from netcdf_to_gltf_converter.netcdf.wrapper import UgridDataset, UgridVariable
from netcdf_to_gltf_converter.preprocessing.interpolation import Interpolator, Location
from netcdf_to_gltf_converter.preprocessing.transformation import Transformer
from netcdf_to_gltf_converter.preprocessing.triangulation import Triangulator
from netcdf_to_gltf_converter.utils.arrays import uint32_array
from netcdf_to_gltf_converter.utils.sequences import inclusive_range


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
        triangulated_grid = self._triangulator.triangulate(ugrid_dataset.ugrid2d)

        triangular_meshes = []

        for variable in config.variables:
            data_mesh = self.parse_variable(
                variable, triangulated_grid, ugrid_dataset, config
            )
            triangular_meshes.append(data_mesh)

            if variable.use_threshold:
                threshold_mesh = data_mesh.get_threshold_mesh(
                    variable.threshold_height * config.scale, variable.threshold_color
                )
                triangular_meshes.append(threshold_mesh)

        return triangular_meshes

    def parse_variable(
        self,
        variable: Variable,
        grid: Ugrid2d,
        ugrid_dataset: UgridDataset,
        config: Config,
    ):
        data = ugrid_dataset.get_ugrid_variable(variable.name)
        interpolated_data = self._interpolate(
            data.coordinates, data.get_data_at_time(config.time_index_start), grid
        )

        base = MeshAttributes(
            vertex_positions=interpolated_data, mesh_color=variable.color
        )
        triangles = uint32_array(grid.face_node_connectivity)
        transformations = list(
            self._get_transformations(data, grid, base, variable.color, config)
        )

        return TriangularMesh(
            base=base,
            triangles=triangles,
            transformations=transformations,
        )

    def _interpolate(
        self, data_coords: np.ndarray, data_values: np.ndarray, grid: Ugrid2d
    ):
        return self._interpolator.interpolate_nearest(
            data_coords, data_values, grid, Location.nodes
        )

    def _get_transformations(
        self,
        data: UgridVariable,
        grid: Ugrid2d,
        base: MeshAttributes,
        color: Color,
        config: Config,
    ) -> Generator[MeshAttributes, None, None]:
        time_index_start = config.time_index_start + config.times_per_frame
        if config.time_index_end is not None:
            time_index_end = config.time_index_end
        else:
            time_index_end = data.time_index_max

        for time_index in inclusive_range(
            time_index_start, time_index_end, config.times_per_frame
        ):
            interpolated_data = self._interpolate(
                data.coordinates, data.get_data_at_time(time_index), grid
            )
            vertex_displacements = np.subtract(
                interpolated_data,
                base.vertex_positions,
                dtype=np.float32,
            )

            yield MeshAttributes(
                vertex_positions=vertex_displacements, mesh_color=color
            )
