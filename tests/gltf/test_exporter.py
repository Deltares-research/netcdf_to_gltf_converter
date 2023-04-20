from pathlib import Path

import pytest
from netcdf_to_gltf_converter.gltf.exporter import Exporter
from pygltflib import GLTF2

from tests.utils import get_temp_file


class TestExporter():
    def test_export_with_invalid_file_type(self):
        gltf = GLTF2()
        file = Path("file.invalid")
        
        with pytest.raises(ValueError) as error:
            Exporter.export(gltf, file)
            
        assert str(error.value) == "GLTF file cannot be exported: unsupported file type '.invalid'. Supported: .gltf, .glb"
        
    def test_export_with_glb_file(self):
        gltf = GLTF2()
        
        with get_temp_file("file.glb") as file:
            Exporter.export(gltf, file)
            assert file.is_file()
            
    def test_export_with_gltf_file(self):
        gltf = GLTF2()
        
        with get_temp_file("file.gltf") as file:
            Exporter.export(gltf, file)
            assert file.is_file()