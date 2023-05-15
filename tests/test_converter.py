from pathlib import Path

import pytest

from netcdf_to_gltf_converter.converter import Converter
from tests.utils import assert_files_equal, get_temp_file, reference_files, resources


class TestConverter:
    def test_initialize_netcdf_does_not_exist_raises_error(self):
        netcdf = Path("path/to/file.netcdf")
        gltf = Path("path/to/file.gltf")
        config = Path("path/to/file.json")

        with pytest.raises(ValueError) as error:
            _ = Converter(netcdf, gltf, config)

        assert str(error.value) == rf"NetCDF file does not exist: {netcdf}"
        
    def test_initialize_config_does_not_exist_raises_error(self):
        netcdf = resources / "3x3nodes_rectilinear_map.nc"
        gltf = Path("path/to/file.gltf")
        config = Path("path/to/file.json")

        with pytest.raises(ValueError) as error:
            _ = Converter(netcdf, gltf, config)

        assert str(error.value) == rf"Config file does not exist: {config}"
            
    def test_run(self):
        netcdf = resources / "3x3nodes_rectilinear_map.nc"
        reference_gltf = reference_files / "3x3nodes_rectilinear_map.gltf"
        config = resources / "config.json"

        with get_temp_file(reference_gltf.name) as gltf:
            converter = Converter(netcdf, gltf, config)
            converter.run()

            assert_files_equal(gltf, reference_gltf)
