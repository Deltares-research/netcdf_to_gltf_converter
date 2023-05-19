import xugrid as xu
from xugrid.ugrid.connectivity import triangulate as triangulate_grid


def triangulate(grid: xu.Ugrid2d) -> xu.Ugrid2d:
    """Triangulate the provided UGrid 2D.

    Args:
        ugrid2d (xu.Ugrid2d): The UGrid 2D to triangulate.

    Returns:
        xu.Ugrid2d: The triangulated UGrid 2D.
    """
    face_node_connectivity, _ = triangulate_grid(
        grid.face_node_connectivity, fill_value=grid.fill_value
    )
    return xu.Ugrid2d(grid.node_x, grid.node_y, grid.fill_value, face_node_connectivity)
