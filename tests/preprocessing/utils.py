import numpy as np
import xugrid as xu

from netcdf_to_gltf_converter.netcdf.dflowfm.wrapper import Ugrid


class Factory:
    @staticmethod
    def create_rectilinear_grid() -> Ugrid:
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
        face_node_connectivity = np.array(
            [[0, 1, 4, 3], [1, 2, 5, 4], [3, 4, 7, 6], [4, 5, 8, 7]]
        )

        ugrid2d = xu.Ugrid2d(node_x, node_y, fill_value, face_node_connectivity)
        return Ugrid(ugrid2d)
