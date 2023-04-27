import numpy as np

from netcdf_to_gltf_converter.data.mesh import MeshGeometry, TriangularMesh


class TestTriangularMesh:
    def test_initializer(self):
        vertex_positions = np.array(
            [
                [0, 0, 1],
                [1, 0, 2],
                [1, 1, 3],
                [0, 1, 4],
            ],
            dtype="float32",
        )
        mesh_geometry = MeshGeometry(vertex_positions=vertex_positions)

        triangles = np.array(
            [
                [0, 1, 2],
                [0, 2, 3],
            ],
            dtype="uint32",
        )

        mesh_transformation = MeshGeometry(
            vertex_positions=np.array(
                [
                    [0, 0, 0.5],
                    [0, 0, -0.5],
                    [0, 0, 0.5],
                    [0, 0, -1.0],
                ],
                dtype="float32",
            )
        )

        triangular_mesh = TriangularMesh(
            mesh_geometry, triangles, [mesh_transformation]
        )

        assert triangular_mesh.mesh_geometry == mesh_geometry
        np.array_equal(triangular_mesh.triangles, triangles)
        assert len(triangular_mesh.mesh_transformations) == 1
        assert triangular_mesh.mesh_transformations[0] == mesh_transformation
