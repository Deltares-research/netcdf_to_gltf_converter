from pathlib import Path

import pytest

from netcdf_to_gltf_converter.converter import Converter


class TestConverter:
    def test_initialize_netcdf_does_not_exist_raises_error(self):
        netcdf = Path("path/to/file.netcdf")
        gltf = Path("path/to/file.gltf")
        
        with pytest.raises(ValueError) as error:
            _ = Converter(netcdf, gltf)
            
        assert str(error.value) == rf"NetCDF file does not exist: {netcdf}"