from pathlib import Path

from netcdf_to_gltf_converter.config import Config
from netcdf_to_gltf_converter.gltf.builder import GLTFBuilder
from netcdf_to_gltf_converter.gltf.exporter import Exporter
from netcdf_to_gltf_converter.netcdf.importer import Importer


class Converter:
    """Converter class for converting the NetCDF file to a glTF file."""

    def __init__(self, netcdf: Path, gltf: Path, config: Path) -> None:
        """Initialize a Converter with the specified arguments.

        Args:
            netcdf (Path): Path to the source NetCDF file.
            gltf (Path): Path to the destination glTF file.
            config (Path): Path to the converter configuration file.

        Raises:
            ValueError: When the NetCDF or configuration file does not exist.
        """

        if not netcdf.is_file():
            raise ValueError(f"NetCDF file does not exist: {netcdf}")
        if not config.is_file():
            raise ValueError(f"Config file does not exist: {config}")

        self._netcdf = netcdf
        self._gltf = gltf
        self._config = Config.from_file(config)

        self._importer = Importer()

    def run(self):
        """Run the conversion."""

        triangular_meshes = self._importer.import_from(self._netcdf, self._config)

        builder = GLTFBuilder()
        for triangular_grid in triangular_meshes:
            builder.add_triangular_mesh(triangular_grid)

        gltf = builder.finish()

        Exporter.export(gltf, self._gltf)
