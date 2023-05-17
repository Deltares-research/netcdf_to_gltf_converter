from pathlib import Path
from typing import List

import xarray as xr

from netcdf_to_gltf_converter.config import Config
from netcdf_to_gltf_converter.data.mesh import TriangularMesh
from netcdf_to_gltf_converter.netcdf.parser import Parser


class Importer:
    """Class to import TriangularMeshes from a source file."""

    def __init__(self) -> None:
        """Initialize an Importer."""
        self._parser = Parser()

    def import_from(self, file_path: Path, config: Config) -> List[TriangularMesh]:
        """Imports triangular meshes from the given NetCDF file.

        Args:
            file_path (Path): Path to the source NetCDF file.
            config (Path): Path to the converter configuration file.

        Returns:
            List[TriangularMesh]: The list of imported triangular meshes.

        Raises:
            ValueError: When the NetCDF file does not exist.
        """
        if not file_path.is_file():
            raise ValueError(f"NetCDF file does not exist: {file_path}")

        ds = xr.open_dataset(str(file_path))
        return self._parser.parse(ds, config)
