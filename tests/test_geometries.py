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

        triangle.node_index_1 == node_index_1
        triangle.node_index_2 == node_index_2
        triangle.node_index_3 == node_index_3
        
    def test_as_list(self):
        node_index_1 = 0
        node_index_2 = 2
        node_index_3 = 4
        triangle = Triangle(node_index_1, node_index_2, node_index_3)
        
        as_list = triangle.as_list()
        
        assert as_list == [node_index_1, node_index_2, node_index_3]


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
