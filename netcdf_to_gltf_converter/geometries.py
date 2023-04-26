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

    @staticmethod
    def from_array(array: np.ndarray) -> "Vec3":
        """Create a Vec3 from the given data.

        Args:
            array (np.ndarray): The vector values, a 1D ndarray of floats with shape (3, ) containing the three vector values.

        Returns:
            Vec3: The constructed Vec3 object.
        """
        return Vec3(x=array[0], y=array[1], z=array[2])


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

    @staticmethod
    def from_array(array: np.ndarray) -> "Triangle":
        """Create a Triangle from the given data.

        Args:
            array (np.ndarray): The node indices of the triangle, a 1D ndarray of floats with shape (3, ) containing the three node indices.

        Returns:
            Vec3: The constructed Vec3 object.
        """
        return Triangle(
            node_index_1=array[0], node_index_2=array[1], node_index_3=array[2]
        )


MeshGeometry = List[Node]


class TriangularMesh:
    def __init__(
        self,
        nodes: MeshGeometry,
        triangles: List[Triangle],
        node_transformations: List[MeshGeometry] = None,
    ) -> None:
        """Initialize a TriangularMesh with the given arguments.

        Args:
            nodes (List[Node]): The nodes in the mesh.
            triangles (List[Triangle]): The triangles in the mesh each containing the three node indices that define the triangle shape and position.
            node_transformations (List[List[[Node]]): The collection of node transformations.
        """
        self.nodes = nodes
        self.triangles = triangles
        self.node_transformations = node_transformations

    def nodes_positions_as_array(self) -> np.ndarray:
        """Gets a two-dimensional array where each row contains three values that represent the x, y and z positions of a node.
        Note that this array is not cached and will be rebuilt with each call.

        Returns:
            np.ndarray: A two-dimensional numpy array with data type 'float32'.
        """
        positions = [node.position.as_list() for node in self.nodes]
        return np.array(positions, dtype="float32")

    def triangles_as_array(self) -> np.ndarray:
        """Gets a two-dimensional array where each row contains three values that represent the node indices of a triangle.
        Note that this array is not cached and will be rebuilt with each call.

        Returns:
            np.ndarray: A two-dimensional numpy array with data type 'uint16'.
        """
        triangles = [triangle.as_list() for triangle in self.triangles]
        return np.array(triangles, dtype="uint32")

    def node_transformations_as_array(self) -> np.ndarray:
        nodes_transformations_arr = []
        for nodes_transformation in self.node_transformations:
            nodes_transformation_arr = [
                node.position.as_list() for node in nodes_transformation
            ]
            nodes_transformations_arr.append(nodes_transformation_arr)

        return np.array(nodes_transformations_arr, dtype="float32")

    @staticmethod
    def from_arrays(
        nodes_arr: np.ndarray,
        indices_arr: np.ndarray,
        node_transformations_arr: List[np.ndarray],
    ) -> "TriangularMesh":
        """Create a triangular mesh from the given data.

        Args:
            nodes_arr (np.ndarray): The node coordinates, a 2D ndarray of floats with shape (n, 3) where each row contains the x, y and z coordinate.
            indices_arr (np.ndarray): The face node indices, a 2D ndarray of floats with shape (m, 3) where each row contains three node indices that define the triangle shape and position.
            nodes_arr (np.ndarray): The node coordinate transformations, a 2D ndarray of floats with shape (n, 3) where each row contains the x, y and z coordinate transformations.
        Returns:
            TriangularMesh: The constructed triangular mesh object.
        """

        nodes = [Node(Vec3.from_array(xyz)) for xyz in nodes_arr]
        triangles = [
            Triangle.from_array(triangle_indices) for triangle_indices in indices_arr
        ]

        node_transformations: List[MeshGeometry] = []

        for node_transformation in node_transformations_arr:
            mesh_geom = [Node(Vec3.from_array(xyz)) for xyz in node_transformation]
            node_transformations.append(mesh_geom)

        return TriangularMesh(nodes, triangles, node_transformations)
