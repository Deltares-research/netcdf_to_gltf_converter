from pathlib import Path

import pytest
from pygltflib import GLTF2

from netcdf_to_gltf_converter.gltf.exporter import Exporter
from tests.utils import get_temp_file


class TestExporter:
    def test_export_with_invalid_file_type(self):
        gltf = GLTF2()
        file_path = Path("file.invalid")
        exporter = Exporter()
        
        with pytest.raises(ValueError) as error:
            exporter.export(gltf, file_path)

        assert (
            str(error.value)
            == "GLTF file cannot be exported: unsupported file type '.invalid'. Supported: .gltf, .glb"
        )

    def test_export_with_glb_file(self):
        gltf = GLTF2()
        exporter = Exporter()

        with get_temp_file("file.glb") as file_path:
            exporter.export(gltf, file_path)
            assert file_path.is_file()

    def test_export_with_gltf_file(self):
        gltf = GLTF2()
        exporter = Exporter()

        with get_temp_file("file.gltf") as file_path:
            exporter.export(gltf, file_path)
            assert file_path.is_file()
