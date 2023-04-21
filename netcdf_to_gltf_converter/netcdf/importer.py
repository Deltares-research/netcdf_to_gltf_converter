from enum import Enum
from pathlib import Path
from typing import List
import xugrid as xu
import xarray as xr
from netcdf_to_gltf_converter.geometries import Node, Triangle, TriangularMesh, Vec3
import random

class MeshType(str, Enum):
    """Enum containg the valid mesh types as stored in the "mesh" attribute of a data variable."""

    mesh1d = "mesh1d"
    """1D mesh"""
    mesh2d = "Mesh2d"
    """2D mesh"""
    
class StandardName(str, Enum):
    """Enum containg the valid variable standard names according to the
    NetCDF Climate and Forecast (CF) Metadata Conventions version 1.8.
    See also: http://cfconventions.org/Data/cf-standard-names/current/build/cf-standard-name-table.html
    """

    water_depth = "sea_floor_depth_below_sea_surface"
    """The vertical distance between the sea surface and the seabed as measured at a given point in space including the variance caused by tides and possibly waves."""

class Importer:

    def _filter_by_mesh(ds: xr.Dataset, mesh: MeshType):
        return ds.filter_by_attrs(mesh=mesh)

    def _filter_by_standard_name(ds: xr.Dataset, standard_name: str):
        filter = {"standard_name":StandardName.water_depth}
        return ds.filter_by_attrs(**filter)

    def _get_water_depth_2d(ugrid_ds: xu.UgridDataset) -> xr.DataArray:
        ds_mesh2d: xr.Dataset = Importer._filter_by_mesh(ugrid_ds, MeshType.mesh2d)
        ds_water_depth: xr.DataArray = Importer._filter_by_standard_name(ds_mesh2d, StandardName.water_depth)

        return ds_water_depth    
    
    def _get_nodes_from_ugrid2d(grid: xu.Ugrid2d) -> List[Node]:
        nodes: List[Node] = []
        for i in range(grid.n_node):
            x = grid.node_x[i]
            y = grid.node_y[i]
            z = random.random()
        
            node = Node(position=Vec3(x, y, z))
            nodes.append(node)
        
        return nodes
    
    def _get_triangles_from_ugrid2d(grid: xu.Ugrid2d) -> List[Triangle]:
        triangles: List[Triangle] = []
        
        for face_node_indices in grid.face_node_connectivity:
            assert len(face_node_indices) == 3
            
            i1 = face_node_indices[0]
            i2 = face_node_indices[1]
            i3 = face_node_indices[2]
            
            triangle = Triangle(i1, i2, i3)
            triangles.append(triangle)
    
        return triangles
    
         
    @staticmethod
    def import_from(file_path: Path) -> TriangularMesh:
        ugrid_ds: xu.UgridDataset = xu.open_dataset(str(file_path))
        ds = xr.open_dataset(str(file_path))
        
        ds_water_depth = Importer._get_water_depth_2d(ugrid_ds)
    
        ugrid2d = xu.Ugrid2d.from_dataset(ds, MeshType.mesh2d)
        triangulated_ugrid2d = ugrid2d.triangulate()
    
        nodes = Importer._get_nodes_from_ugrid2d(triangulated_ugrid2d)
        triangles = Importer._get_triangles_from_ugrid2d(triangulated_ugrid2d)
        
        triangular_mesh = TriangularMesh(nodes=nodes, triangles=triangles)
        return triangular_mesh
