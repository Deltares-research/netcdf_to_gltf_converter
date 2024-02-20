from typing import List

import numpy as np
import xarray as xr

from netcdf_to_gltf_converter.config import Config, ModelType, Variable
from netcdf_to_gltf_converter.data.mesh import MeshAttributes, TriangularMesh
from netcdf_to_gltf_converter.netcdf.ugrid.wrapper import UgridDataset
from netcdf_to_gltf_converter.netcdf.xbeach.wrapper import XBeachDataset
from netcdf_to_gltf_converter.netcdf.wrapper import (
    DatasetWrapper,
    GridWrapper,
    VariableWrapper,
)
from netcdf_to_gltf_converter.preprocessing.interpolation import (
    NearestPointInterpolator,
)
from netcdf_to_gltf_converter.preprocessing.transformation import scale, shift
from netcdf_to_gltf_converter.preprocessing.triangulation import triangulate
from netcdf_to_gltf_converter.utils.arrays import uint32_array
from netcdf_to_gltf_converter.utils.sequences import inclusive_range


class Parser:
    """Class to parse a xr.DataArray into a set of TriangularMeshes."""

    def __init__(self) -> None:
        """Initialize a Parser."""

        self._interpolator = NearestPointInterpolator()

    def parse(self, dataset: xr.Dataset, config: Config) -> List[TriangularMesh]:
        """Parse the provided data set to a list of TriangularMeshes.

        Args:
            dataset (xr.Dataset): The NetCDF dataset.
            config (Config): The converter configuration.
        """
        if config.model_type == ModelType.DHYDRO:
            dataset = UgridDataset(dataset)
        elif config.model_type == ModelType.XBEACH:
            dataset = XBeachDataset(dataset)
        
        Parser._transform_grid(config, dataset)

        grid = dataset.grid
        triangulate(grid)

        triangular_meshes = []

        for variable in config.variables:
            data_mesh = self._parse_variable(variable, grid, dataset, config)
            triangular_meshes.append(data_mesh)

            if variable.use_threshold:
                threshold_mesh = data_mesh.get_threshold_mesh(
                    variable.threshold_height * config.scale_vertical,
                    variable.threshold_color,
                )
                triangular_meshes.append(threshold_mesh)

        return triangular_meshes

    def _parse_variable(
        self,
        variable: Variable,
        grid: GridWrapper,
        ugrid_dataset: DatasetWrapper,
        config: Config,
    ):
        data = ugrid_dataset.get_variable(variable.name)
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

        return TriangularMesh(
            base,
            triangles,
            transformations,
            variable.metallic_factor,
            variable.roughness_factor,
        )

    @staticmethod
    def _get_time_indices(time_index_max: int, config: Config):
        start = config.time_index_start + config.times_per_frame

        if config.time_index_end is not None:
            end = config.time_index_end
        else:
            end = time_index_max

        return inclusive_range(start, end, config.times_per_frame)

    @staticmethod
    def _transform_grid(config: Config, dataset: DatasetWrapper):
        if config.shift_coordinates:
            shift(dataset)

        variables = [var.name for var in config.variables]
        scale(dataset, variables, config.scale_horizontal, config.scale_vertical)

    def _interpolate(self, data: VariableWrapper, time_index: int, grid: GridWrapper):
        return self._interpolator.interpolate(
            data.coordinates, data.get_data_at_time(time_index), grid
        )

    @staticmethod
    def calculate_displacements(data: np.ndarray, base: MeshAttributes):
        return np.subtract(
            data,
            base.vertex_positions,
            dtype=np.float32,
        )
