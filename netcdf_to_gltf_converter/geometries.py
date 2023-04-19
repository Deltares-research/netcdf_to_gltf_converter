from typing import List
import numpy as np

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
      
    def as_list(self):
        return [self.x, self.y, self.z]


class Node:
    def __init__(self, position: Vec3) -> None:
        """Initialize a Node with the given arguments.

        Args:
            position (Vec3): The position of the node defined by the x, y and z direction.
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
        
    def as_list(self):
        return [self.node_index_1, self.node_index_2, self.node_index_3]


class TriangularMesh:
    def __init__(self, nodes: List[Node], triangles: List[Triangle]) -> None:
        """Initialize a TriangularMesh with the given arguments.

        Args:
            nodes (List[Node]): The nodes in the mesh.
            triangles (List[Triangle]): The triangles in the mesh each containing the three node indices that define the triangle shape and position. 
        """
        self.nodes = nodes
        self.triangles = triangles
   
    def nodes_positions_as_array(self) -> np.array:
        """Gets a two-dimensional array where each row contains three values that represent the x, y and z positions of a node.
        Note that this array is not cached and will be rebuilt with each call.

        Returns:
            np.array: A two-dimensional numpy array with data type 'float32'.
        """
        positions = [node.position.as_list() for node in self.nodes]
        return np.array(positions, dtype="float32")

    def triangles_as_array(self) -> np.array:
        """Gets a two-dimensional array where each row contains three values that represent the node indices of a triangle.
        Note that this array is not cached and will be rebuilt with each call.

        Returns:
            np.array: A two-dimensional numpy array with data type 'uint8'.
        """
        triangles = [triangle.as_list() for triangle in self.triangles]
        return np.array(triangles, dtype="uint8")