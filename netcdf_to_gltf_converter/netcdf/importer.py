from pathlib import Path

import xarray as xr

from netcdf_to_gltf_converter.data.mesh import TriangularMesh
from netcdf_to_gltf_converter.netcdf.wrapper import Wrapper


class Importer:
    @staticmethod
    def import_from(file_path: Path) -> TriangularMesh:
        """Imports the dataset from the given NetCDF file.

        Args:
            file_path (Path): Path to the source NetCDF file.

        Returns:
            xr.Dataset: The data set from the NetCDF file.

        Raises:
            ValueError: When the NetCDF file does not exist.
        """
        if not file_path.is_file():
            raise ValueError(f"NetCDF file does not exist: {file_path}")

        ds = xr.open_dataset(str(file_path))
        wrapper = Wrapper(ds)
        return wrapper.to_triangular_mesh()
