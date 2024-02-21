from xugrid.ugrid.connectivity import triangulate as triangulate_grid

from netcdf_to_gltf_converter.netcdf.netcdf_data import DatasetBase


def triangulate(dataset: DatasetBase):
    """Triangulate the provided grid.

    Args:
        dataset (DatasetBase): The grid to triangulate.
    """

    face_node_connectivity, _ = triangulate_grid(
        dataset.face_node_connectivity, dataset.fill_value
    )
    dataset.set_face_node_connectivity(face_node_connectivity)
