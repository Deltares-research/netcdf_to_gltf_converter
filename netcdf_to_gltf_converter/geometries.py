from typing import List


class Vec3:
    def __init__(self, x: float, y: float, z: float) -> None:
        """Initialize a Vec3 with the given arguments.

        Args:
            x (float): The x value.
            y (float): The y value.
            z (float): The z value.
        """
        self.x = x
        self.y = y
        self.z = z


class Node:
    def __init__(self, position: Vec3) -> None:
        """Initialize a Node with the given arguments.

        Args:
            position (Vec3): The position described by a 3D vector.
        """
        self.position = position


class Triangle:
    def __init__(self, node_index_1: int, node_index_2: int, node_index_3: int) -> None:
        """Initialize a Triangle with the given arguments.

        Args:
            node_index_1 (int): The index of the first node.
            node_index_2 (int): The index of the second node.
            node_index_3 (int): The index of the third node.
        """
        self.node_index_1 = node_index_1
        self.node_index_2 = node_index_2
        self.node_index_3 = node_index_3


class TriangularMesh:
    def __init__(self, nodes: List[Node], triangles: List[Triangle]) -> None:
        """Initialize a TriangularMesh with the given arguments.

        Args:
            nodes (List[Node]): The nodes in the mesh.
            triangles (List[Triangle]): The triangles in the mesh containing the three node indices that define the triangle shape and position.
        """
        self.nodes = nodes
        self.triangles = triangles
