from pathlib import Path
from typing import List

import xarray as xr

from netcdf_to_gltf_converter.data.mesh import TriangularMesh
from netcdf_to_gltf_converter.netcdf.wrapper import StandardName, Wrapper


class Importer:
    @staticmethod
    def import_from(file_path: Path) -> List[TriangularMesh]:
        """Imports triangular meshes from the given NetCDF file.

        Args:
            file_path (Path): Path to the source NetCDF file.

        Returns:
            List[TriangularMesh]: The list of imported triangular meshes.

        Raises:
            ValueError: When the NetCDF file does not exist.
        """
        if not file_path.is_file():
            raise ValueError(f"NetCDF file does not exist: {file_path}")

        ds = xr.open_dataset(str(file_path))
        wrapper = Wrapper(ds)
        water_depth_mesh = wrapper.to_triangular_mesh(standard_name=StandardName.water_depth)
        threshold_mesh = water_depth_mesh.get_threshold_mesh(height=0.01)
        
        return [water_depth_mesh, threshold_mesh]
