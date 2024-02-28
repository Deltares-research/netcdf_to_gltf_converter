import logging
from datetime import datetime
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
        self._exporter = Exporter()
        
        self._configure_logging()

    def _configure_logging(self) -> None:
        self._reset_logger()
        
        time_stamp = datetime.now().strftime("%y%m%d_%H%M%S")
        log_file = self._gltf.parent / f"gltf_converter_{time_stamp}.log"
        
        logging.basicConfig(
            level=logging.DEBUG,
            filename=log_file,
            filemode="w",
            format="%(asctime)s %(levelname)-8s %(filename)-20s %(funcName)-30s %(message)s",
            datefmt="%H:%M:%S",
        )

    def _reset_logger(self):
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
            
    def run(self):
        """Run the conversion."""

        triangular_meshes = self._importer.import_from(self._netcdf, self._config)

        builder = GLTFBuilder()
        for triangular_grid in triangular_meshes:
            builder.add_triangular_mesh(triangular_grid)

        gltf = builder.finish()

        self._exporter.export(gltf, self._gltf)
