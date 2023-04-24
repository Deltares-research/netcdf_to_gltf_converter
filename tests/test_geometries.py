import numpy as np

from netcdf_to_gltf_converter.geometries import Node, Triangle, TriangularMesh, Vec3


class TestVec3:
    def test_initializer(self):
        x = 1.23
        y = 2.34
        z = 3.45

        vec3 = Vec3(x, y, z)

        assert vec3.x == x
        assert vec3.y == y
        assert vec3.z == z

    def test_as_list(self):
        x = 1.23
        y = 2.34
        z = 3.45
        vec3 = Vec3(x, y, z)

        as_list = vec3.as_list()

        assert as_list == [x, y, z]

    def test_from_array(self):
        array = [1,2,3]
        
        vec3 = Vec3.from_array(array)
        
        assert vec3.x == 1
        assert vec3.y == 2
        assert vec3.z == 3
        

class TestNode:
    def test_initializer(self):
        position = Vec3(1.23, 2.34, 3.45)

        node = Node(position)

        assert node.position == position


class TestTriangle:
    def test_initializer(self):
        node_index_1 = 0
        node_index_2 = 2
        node_index_3 = 4

        triangle = Triangle(node_index_1, node_index_2, node_index_3)

        assert triangle.node_index_1 == node_index_1
        assert triangle.node_index_2 == node_index_2
        assert triangle.node_index_3 == node_index_3

    def test_as_list(self):
        node_index_1 = 0
        node_index_2 = 2
        node_index_3 = 4
        triangle = Triangle(node_index_1, node_index_2, node_index_3)

        as_list = triangle.as_list()

        assert as_list == [node_index_1, node_index_2, node_index_3]

    def test_from_array(self):
        array = [1,2,3]
        
        triangle = Triangle.from_array(array)
        
        assert triangle.node_index_1 == 1
        assert triangle.node_index_2 == 2
        assert triangle.node_index_3 == 3

class TestTriangularMesh:
    def test_initializer(self):
        nodes = [
            Node(position=Vec3(0, 0, 1)),
            Node(position=Vec3(1, 0, 2)),
            Node(position=Vec3(1, 1, 3)),
            Node(position=Vec3(0, 1, 4)),
        ]

        triangles = [
            Triangle(0, 1, 2),
            Triangle(0, 2, 3),
        ]

        triangular_mesh = TriangularMesh(nodes, triangles)

        assert triangular_mesh.nodes == nodes
        assert triangular_mesh.triangles == triangles

    def test_nodes_positions_as_array(self):
        nodes = [
            Node(position=Vec3(0, 0, 1)),
            Node(position=Vec3(1, 0, 2)),
            Node(position=Vec3(1, 1, 3)),
            Node(position=Vec3(0, 1, 4)),
        ]

        triangles = [
            Triangle(0, 1, 2),
            Triangle(0, 2, 3),
        ]

        triangular_mesh = TriangularMesh(nodes, triangles)

        array = triangular_mesh.nodes_positions_as_array()

        exp_array = [[0, 0, 1], [1, 0, 2], [1, 1, 3], [0, 1, 4]]

        assert np.array_equal(array, exp_array)
        assert array.dtype == "float32"

    def test_triangles_as_array(self):
        nodes = [
            Node(position=Vec3(0, 0, 1)),
            Node(position=Vec3(1, 0, 2)),
            Node(position=Vec3(1, 1, 3)),
            Node(position=Vec3(0, 1, 4)),
        ]

        triangles = [
            Triangle(0, 1, 2),
            Triangle(0, 2, 3),
        ]

        triangular_mesh = TriangularMesh(nodes, triangles)

        array = triangular_mesh.triangles_as_array()

        exp_array = [[0, 1, 2], [0, 2, 3]]

        assert np.array_equal(array, exp_array)
        assert array.dtype == "uint32"

    def test_from_arrays(self):
        nodes_arr = [[0,0,1],[1,0,2],[0,1,3]]
        indices_arr = [[0,1,2]]
        
        triangular_mesh = TriangularMesh.from_arrays(nodes_arr, indices_arr)
        
        nodes = [node.position.as_list() for node in triangular_mesh.nodes]
        indices = [triangle.as_list() for triangle in triangular_mesh.triangles]
        
        np.array_equal(nodes, nodes_arr)
        np.array_equal(indices, indices_arr)