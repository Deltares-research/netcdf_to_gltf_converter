from pathlib import Path

from netcdf_to_gltf_converter.gltf.builder import GLTFBuilder
from netcdf_to_gltf_converter.gltf.exporter import Exporter
from netcdf_to_gltf_converter.netcdf.importer import Importer


class Converter:
    """Converter class for converting the NetCDF file to a glTF file."""

    def __init__(self, netcdf: Path, gltf: Path) -> None:
        """Initialize a Converter with the specified arguments.

        Args:
            netcdf (Path): Path to the source NetCDF file
            gltf (Path): Path to the destination glTF file

        Raises:
            ValueError: When the NetCDF file does not exist.
        """

        if not netcdf.is_file():
            raise ValueError(f"NetCDF file does not exist: {netcdf}")

        self._netcdf = netcdf
        self._gltf = gltf

    def run(self):
        """Run the conversion."""

        triangular_grid = Importer.import_from(self._netcdf)

        builder = GLTFBuilder()
        builder.add_triangular_mesh(triangular_grid)
        gltf = builder.finish()

        Exporter.export(gltf, self._gltf)
