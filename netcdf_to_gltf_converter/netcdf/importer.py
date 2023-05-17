from pathlib import Path
from typing import List

import xarray as xr

from netcdf_to_gltf_converter.config import Config
from netcdf_to_gltf_converter.data.mesh import TriangularMesh
from netcdf_to_gltf_converter.netcdf.parser import Parser


class Importer:
    @staticmethod
    def import_from(file_path: Path, config: Config) -> List[TriangularMesh]:
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
        parser = Parser(ds, config)

        triangular_meshes = []

        for variable in config.variables:
            data_mesh = parser.to_triangular_mesh(variable.name)
            triangular_meshes.append(data_mesh)

            if variable.use_threshold:
                threshold_mesh = data_mesh.get_threshold_mesh(
                    variable.threshold_height * config.scale, 
                    variable.threshold_color
                )
                triangular_meshes.append(threshold_mesh)

        return triangular_meshes
