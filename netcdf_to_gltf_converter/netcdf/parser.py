import logging
from typing import List, Tuple

import numpy as np
import xarray as xr

from netcdf_to_gltf_converter.config import Config, CrsShifting, ModelType, ShiftType, Variable
from netcdf_to_gltf_converter.data.mesh import MeshAttributes, TriangularMesh
from netcdf_to_gltf_converter.preprocessing.crs import create_crs_transformer
from netcdf_to_gltf_converter.netcdf.netcdf_data import (DatasetBase,
                                                         DataVariable)
from netcdf_to_gltf_converter.netcdf.ugrid.ugrid_data import UgridDataset
from netcdf_to_gltf_converter.netcdf.xbeach.xbeach_data import XBeachDataset
from netcdf_to_gltf_converter.preprocessing.interpolation import \
    NearestPointInterpolator
from netcdf_to_gltf_converter.utils.arrays import uint32_array
from netcdf_to_gltf_converter.utils.sequences import inclusive_range


class Parser:
    """Class to parse a xr.DataArray into a set of TriangularMeshes."""

    def __init__(self) -> None:
        """Initialize a Parser."""

        self._interpolator = NearestPointInterpolator()

    def parse(self, netcdf_dataset: xr.Dataset, config: Config) -> List[TriangularMesh]:
        """Parse the provided data set to a list of TriangularMeshes as input for building the glTF data.

        Args:
            netcdf_dataset (xr.Dataset): The NetCDF dataset.
            config (Config): The converter configuration.
        """
        if config.model_type == ModelType.DHYDRO:
            dataset = UgridDataset(netcdf_dataset)
        elif config.model_type == ModelType.XBEACH:
            dataset = XBeachDataset(netcdf_dataset)
        
        Parser._transform_grid(config, dataset)

        dataset.triangulate()

        triangular_meshes = []

        for variable in config.variables:
            data_mesh = self._parse_variable(variable, dataset, config)
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
        dataset: DatasetBase,
        config: Config,
    ):
        data = dataset.get_variable(variable.name)
        interpolated_data = self._interpolate(data, config.time_index_start, dataset)

        base = MeshAttributes(interpolated_data, variable.color)
        triangles = uint32_array(dataset.face_node_connectivity)
        transformations = []

        for time_index in Parser._get_time_indices(data.time_index_max, config):
            interpolated_data = self._interpolate(data, time_index, dataset)
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
    def _transform_grid(config: Config, dataset: DatasetBase):
        variables = [var.name for var in config.variables]

        if config.shift_coordinates == ShiftType.MIN:
            dataset.shift_coordinates(dataset.min_x, dataset.min_y, 0, variables=[])
        elif isinstance(config.shift_coordinates, CrsShifting):
            shift_x, shift_y, shift_z = Parser._get_shift_values(config.shift_coordinates)
            
            logging.info(f"Shift model coordinates with: {shift_x} (x), {shift_y} (y), {shift_z} (z) ")
            dataset.shift_coordinates(shift_x, shift_y, shift_z, variables)

        dataset.scale_coordinates(config.scale_horizontal, config.scale_vertical, variables)

    def _get_shift_values(shift_config: CrsShifting) -> Tuple[float, float, float]:
        if shift_config.crs_transformation:
            transformer = create_crs_transformer(shift_config.crs_transformation.source_epsg,
                                                 shift_config.crs_transformation.target_epsg)
            
            logging.info(f"Transforming shift values from {transformer.source_crs.name} to {transformer.target_crs.name}")
            return transformer.transform(shift_config.shift_x, shift_config.shift_y, shift_config.shift_z)

        return (shift_config.shift_x, shift_config.shift_y, shift_config.shift_z)

    def _interpolate(self, data: DataVariable, time_index: int, dataset: DatasetBase) -> np.ndarray:
        return self._interpolator.interpolate(
            data.coordinates, data.get_data_at_time(time_index), dataset
        )

    @staticmethod
    def calculate_displacements(data: np.ndarray, base: MeshAttributes):
        return np.subtract(
            data,
            base.vertex_positions,
            dtype=np.float32,
        )
