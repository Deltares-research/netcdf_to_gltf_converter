from pathlib import Path

import pytest
from pygltflib import GLTF2

from netcdf_to_gltf_converter.gltf.exporter import Exporter


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

    def test_export_with_glb_file(self, tmp_path):
        gltf = GLTF2()
        exporter = Exporter()

        file_path = tmp_path / "file.glb"
        exporter.export(gltf, file_path)
        assert file_path.is_file()

    def test_export_with_gltf_file(self, tmp_path):
        gltf = GLTF2()
        exporter = Exporter()

        file_path = tmp_path / "file.gltf"
        exporter.export(gltf, file_path)
        assert file_path.is_file()
