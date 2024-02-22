import numpy as np
import xugrid as xu

from netcdf_to_gltf_converter.netcdf.ugrid.ugrid_data import UgridDataset
import netcdf_to_gltf_converter.preprocessing.connectivity as connectivity

class Factory:
    @staticmethod
    def create_rectilinear_grid() -> UgridDataset:
        """Create a rectilinear grid with 3x3 nodes.

        5--6--7
        |  |  |
        3--4--5
        |  |  |
        0--1--2

        """

        node_x = np.array([0, 1, 2, 0, 1, 2, 0, 1, 2])
        node_y = np.array([0, 0, 0, 1, 1, 1, 2, 2, 2])
        fill_value = -1
        face_node_connectivity = connectivity.face_node_connectivity_from_regular(3, 3)


        ugrid2d = xu.Ugrid2d(node_x, node_y, fill_value, face_node_connectivity)
        return UgridDataset(ugrid2d.to_dataset())
