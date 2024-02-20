from xugrid.ugrid.connectivity import triangulate as triangulate_grid

from netcdf_to_gltf_converter.netcdf.wrapper import GridBase


def triangulate(grid: GridBase):
    """Triangulate the provided grid.

    Args:
        grid (Ugrid): The grid to triangulate.
    """
    face_node_connectivity, _ = triangulate_grid(
        grid.face_node_connectivity, fill_value=grid.fill_value
    )
    grid.set_face_node_connectivity(face_node_connectivity)
