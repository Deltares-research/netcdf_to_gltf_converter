from pathlib import Path

import pytest

from netcdf_to_gltf_converter.converter import Converter
from tests.utils import assert_files_equal, get_temp_file, reference_files, resources


class TestConverter:
    def test_initialize_netcdf_does_not_exist_raises_error(self):
        netcdf = Path("path/to/file.netcdf")
        gltf = Path("path/to/file.gltf")

        with pytest.raises(ValueError) as error:
            _ = Converter(netcdf, gltf)

        assert str(error.value) == rf"NetCDF file does not exist: {netcdf}"

    def test_run(self):
        netcdf_file_path = resources / "3x3nodes_rectilinear_map.nc"
        reference_gltf_file_path = reference_files / "3x3nodes_rectilinear_map.gltf"

        with get_temp_file(reference_gltf_file_path.name) as gltf_file_path:
            converter = Converter(netcdf_file_path, gltf_file_path)
            converter.run()

            assert_files_equal(gltf_file_path, reference_gltf_file_path)

    def test_case(self):
        netcdf_file_path = Path(r"C:\checkouts\TKI5ARVR\DIMR5bij5naar25_V95P2b\my-artifact\dflowfm\output\DFM_map.nc")
        gltf_file_path = Path("case.gltf")

        converter = Converter(netcdf_file_path, gltf_file_path)
        converter.run()