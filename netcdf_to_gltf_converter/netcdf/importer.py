from enum import Enum
from pathlib import Path
from typing import List

import numpy as np
import xarray as xr
import xugrid as xu

from netcdf_to_gltf_converter.geometries import MeshGeometry, TriangularMesh
from netcdf_to_gltf_converter.preprocessing.interpolation import Interpolator, Location
from netcdf_to_gltf_converter.preprocessing.triangulation import Triangulator


class MeshType(str, Enum):
    """Enum containg the valid mesh types as stored in the "mesh" attribute of a data variable."""

    mesh1d = "mesh1d"
    """1D mesh"""
    mesh2d = "Mesh2d"
    """2D mesh"""


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


class Importer:
    @staticmethod
    def _filter_by_mesh(ds: xr.Dataset, mesh: MeshType):
        return ds.filter_by_attrs(mesh=mesh)

    @staticmethod
    def _filter_by_standard_name(ds: xr.Dataset, standard_name: str):
        standard_name_filter = {"standard_name": standard_name}
        return ds.filter_by_attrs(**standard_name_filter)

    @staticmethod
    def _get_water_depth_2d(ugrid_ds: xu.UgridDataset) -> xr.Dataset:
        ds_mesh2d: xr.Dataset = Importer._filter_by_mesh(ugrid_ds, MeshType.mesh2d)
        ds_water_depth: xr.DataArray = Importer._filter_by_standard_name(
            ds_mesh2d, StandardName.water_depth
        )

        return ds_water_depth

    @staticmethod
    def import_from(file_path: Path) -> TriangularMesh:
        ds = xr.open_dataset(str(file_path))
        ugrid2d = xu.Ugrid2d.from_dataset(ds, MeshType.mesh2d)

        triangulated_grid = Triangulator.triangulate(ugrid2d)

        ds_water_depth = Importer._get_water_depth_2d(ds)
        data_x_coords = ds_water_depth.coords["Mesh2d_face_x"].data
        data_y_coords = ds_water_depth.coords["Mesh2d_face_y"].data
        data_coords = np.array([data_x_coords, data_y_coords]).T

        data_values = Importer.get_water_depth_for_time(ds_water_depth, time_index=0)

        interpolated_vertex_positions = Importer.interpolate(
            data_coords, data_values, triangulated_grid
        )
        base_mesh_geometry = MeshGeometry(
            vertex_positions=interpolated_vertex_positions
        )

        mesh_transformations: List[MeshGeometry] = []
        n_times = ds_water_depth.dims["time"]
        for time_index in range(1, n_times):
            data_values = Importer.get_water_depth_for_time(ds_water_depth, time_index)
            interpolated_vertex_positions = Importer.interpolate(
                data_coords, data_values, triangulated_grid
            )
            vertex_displacements = np.array(
                np.subtract(
                    interpolated_vertex_positions, base_mesh_geometry.vertex_positions
                ),
                dtype="float32",
            )
            mesh_transformation = MeshGeometry(vertex_positions=vertex_displacements)
            mesh_transformations.append(mesh_transformation)

        triangular_mesh = TriangularMesh(
            mesh_geometry=base_mesh_geometry,
            triangles=np.array(
                triangulated_grid.face_node_connectivity, dtype="uint32"
            ),
            mesh_transformations=mesh_transformations,
        )
        return triangular_mesh

    @staticmethod
    def get_water_depth_for_time(ds_water_depth, time_index: int):
        ds_water_depth_for_time = ds_water_depth.isel(time=time_index)
        data_values = ds_water_depth_for_time["Mesh2d_waterdepth"].data
        return data_values

    @staticmethod
    def interpolate(data_coords: np.ndarray, data_values: np.ndarray, grid):
        interpolated_vertex_positions = np.array(
            Interpolator.interpolate_nearest(
                data_coords,
                data_values,
                grid,
                Location.nodes,
            ),
            dtype="float32",
        )

        return interpolated_vertex_positions
