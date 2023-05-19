from typing import List

import numpy as np
import xarray as xr
from xugrid import Ugrid2d

from netcdf_to_gltf_converter.config import Config, Variable
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
        Parser._transform_grid(config, ugrid_dataset)
        triangulated_grid = self._triangulator.triangulate(ugrid_dataset.ugrid2d)

        triangular_meshes = []

        for variable in config.variables:
            data_mesh = self._parse_variable(
                variable, triangulated_grid, ugrid_dataset, config
            )
            triangular_meshes.append(data_mesh)

            if variable.use_threshold:
                threshold_mesh = data_mesh.get_threshold_mesh(
                    variable.threshold_height * config.scale, variable.threshold_color
                )
                triangular_meshes.append(threshold_mesh)

        return triangular_meshes

    def _parse_variable(
        self,
        variable: Variable,
        grid: Ugrid2d,
        ugrid_dataset: UgridDataset,
        config: Config,
    ):
        data = ugrid_dataset.get_ugrid_variable(variable.name)
        interpolated_data = self._interpolate(data, config.time_index_start, grid)

        base = MeshAttributes(interpolated_data, variable.color)
        triangles = uint32_array(grid.face_node_connectivity)
        transformations = []

        for time_index in Parser._get_time_indices(data.time_index_max, config):
            interpolated_data = self._interpolate(data, time_index, grid)
            vertex_displacements = Parser.calculate_displacements(
                interpolated_data, base
            )
            transformation = MeshAttributes(vertex_displacements, variable.color)
            transformations.append(transformation)

        return TriangularMesh(base, triangles, transformations, variable.metallic_factor, variable.roughness_factor)

    @staticmethod
    def _get_time_indices(time_index_max: int, config: Config):
        start = config.time_index_start + config.times_per_frame

        if config.time_index_end is not None:
            end = config.time_index_end
        else:
            end = time_index_max

        return inclusive_range(start, end, config.times_per_frame)

    @staticmethod
    def _transform_grid(config, ugrid_dataset):
        tranformer = Transformer(ugrid_dataset, config)
        tranformer.shift()
        tranformer.scale()

    def _interpolate(self, data: UgridVariable, time_index: int, grid: Ugrid2d):
        return self._interpolator.interpolate_nearest(
            data.coordinates, data.get_data_at_time(time_index), grid, Location.nodes
        )

    @staticmethod
    def calculate_displacements(data: np.ndarray, base: MeshAttributes):
        return np.subtract(
            data,
            base.vertex_positions,
            dtype=np.float32,
        )
