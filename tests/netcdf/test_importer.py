from pathlib import Path

import numpy as np
import pytest

from netcdf_to_gltf_converter.config import Config, Threshold, Variable
from netcdf_to_gltf_converter.netcdf.importer import Importer
from tests.utils import resources


class TestImporter:
    def test_import_from(self):
        file_path = resources / "3x3nodes_rectilinear_map.nc"

        variable = Variable(standard_name="sea_floor_depth_below_sea_surface")
        variable.threshold = Threshold(height=0.01, color=[1.0, 1.0, 1.0, 1.0])
        config = Config(shift_coordinates=False, variables=[variable])

        triangular_meshes = Importer.import_from(file_path, config)
        data_mesh = triangular_meshes[0]

        exp_triangles = np.array(
            [
                [5, 2, 0],
                [5, 0, 1],
                [1, 0, 3],
                [1, 3, 6],
                [2, 7, 4],
                [2, 4, 0],
                [0, 4, 8],
                [0, 8, 3],
            ],
            dtype=np.uint32,
        )

        exp_vertex_positions = np.array(
            [
                [1.0, 1.0, 5.0],
                [0.0, 1.0, 5.0],
                [1.0, 0.0, 5.0],
                [1.0, 2.0, 5.0],
                [2.0, 1.0, 4.0],
                [0.0, 0.0, 5.0],
                [0.0, 2.0, 5.0],
                [2.0, 0.0, 4.0],
                [2.0, 2.0, 4.0],
            ],
            dtype=np.float32,
        )

        exp_vertex_transformations = np.array(
            [
                [0.0, 0.0, -1.0],
                [0.0, 0.0, -1.0],
                [0.0, 0.0, -1.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, -1.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 1.0],
            ],
            dtype=np.float32,
        )

        assert np.array_equal(data_mesh.triangles, exp_triangles)
        assert np.array_equal(data_mesh.base.vertex_positions, exp_vertex_positions)
        assert len(data_mesh.transformations) == 4
        assert np.array_equal(
            data_mesh.transformations[2].vertex_positions,
            exp_vertex_transformations,
        )

    def test_import_from_netcdf_does_not_exist_raises_error(self):
        netcdf = Path("path/to/file.netcdf")

        with pytest.raises(ValueError) as error:
            _ = Importer.import_from(
                netcdf, Config(shift_coordinates=False, variables=[])
            )

        assert str(error.value) == rf"NetCDF file does not exist: {netcdf}"
