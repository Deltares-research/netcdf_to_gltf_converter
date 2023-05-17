import numpy as np

from netcdf_to_gltf_converter.data.mesh import MeshAttributes, TriangularMesh
from netcdf_to_gltf_converter.utils.arrays import float32_array, uint32_array


class TestTriangularMesh:
    def test_initializer(self):
        vertex_positions = float32_array(
            [
                [0, 0, 1],
                [1, 0, 2],
                [1, 1, 3],
                [0, 1, 4],
            ]
        )
        base_geometry = MeshAttributes(
            vertex_positions=vertex_positions, mesh_color=[0.38, 0.73, 0.78, 1.0]
        )

        triangles = uint32_array(
            [
                [0, 1, 2],
                [0, 2, 3],
            ]
        )

        transformation = MeshAttributes(
            vertex_positions=float32_array(
                [
                    [0, 0, 0.5],
                    [0, 0, -0.5],
                    [0, 0, 0.5],
                    [0, 0, -1.0],
                ]
            ),
            mesh_color=[0.38, 0.73, 0.78, 1.0],
        )

        triangular_mesh = TriangularMesh(base_geometry, triangles, [transformation])

        assert triangular_mesh.base == base_geometry
        assert np.array_equal(triangular_mesh.triangles, triangles)
        assert len(triangular_mesh.transformations) == 1
        assert triangular_mesh.transformations[0] == transformation

    def test_get_threshold_mesh(self):
        vertex_positions = float32_array(
            [
                [0, 0, 1],
                [1, 0, 2],
                [1, 1, 3],
                [0, 1, 4],
            ]
        )
        base_geometry = MeshAttributes(
            vertex_positions=vertex_positions, mesh_color=[0.38, 0.73, 0.78, 1.0]
        )

        triangles = uint32_array(
            [
                [0, 1, 2],
                [0, 2, 3],
            ]
        )

        transformation = MeshAttributes(
            vertex_positions=float32_array(
                [
                    [0, 0, 0.5],
                    [0, 0, -0.5],
                    [0, 0, 0.5],
                    [0, 0, -1.0],
                ]
            ),
            mesh_color=[0.38, 0.73, 0.78, 1.0],
        )

        triangular_mesh = TriangularMesh(base_geometry, triangles, [transformation])

        exp_vertex_positions = float32_array(
            [
                [0, 0, 0.01],
                [1, 0, 0.01],
                [1, 1, 0.01],
                [0, 1, 0.01],
            ]
        )

        exp_vertex_colors = float32_array(
            [
                [1.0, 1.0, 1.0, 1.0],
                [1.0, 1.0, 1.0, 1.0],
                [1.0, 1.0, 1.0, 1.0],
                [1.0, 1.0, 1.0, 1.0],
            ]
        )

        threshold_mesh = triangular_mesh.get_threshold_mesh(
            height=0.01, color=[1.0, 1.0, 1.0, 1.0]
        )

        assert np.array_equal(threshold_mesh.triangles, triangular_mesh.triangles)
        assert np.array_equal(
            threshold_mesh.base.vertex_positions, exp_vertex_positions
        )
        assert np.array_equal(threshold_mesh.base.vertex_colors, exp_vertex_colors)
        assert len(threshold_mesh.transformations) == 0
