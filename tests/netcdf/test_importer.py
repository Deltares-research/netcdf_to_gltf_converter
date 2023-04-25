import numpy as np
from netcdf_to_gltf_converter.netcdf.importer import Importer
from tests.utils import test_data

class TestImporter:
    def test_import_from(self):
        file_path = test_data / "3x3nodes_rectilinear.nc"
        triangular_grid = Importer.import_from(file_path)
        
        exp_triangles = np.array([
            [5, 2, 0],
            [5, 0, 1],
            [1, 0, 3],
            [1, 3, 6],
            [2, 7, 4],
            [2, 4, 0],
            [0, 4, 8],
            [0, 8, 3]], dtype=np.uint32)
        
        exp_nodes = np.array([
            [1., 1., 3.],
            [0., 1., 3.],
            [1., 0., 3.],
            [1., 2., 1.],
            [2., 1., 3.],
            [0., 0., 3.],
            [0., 2., 1.],
            [2., 0., 3.],
            [2., 2., 1.]], dtype=np.float32)
        
        np.array_equal(triangular_grid.triangles, exp_triangles)
        np.array_equal(triangular_grid.nodes, exp_nodes)