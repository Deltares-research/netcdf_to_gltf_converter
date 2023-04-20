import random
from typing import List

from pygltflib import gltf_asdict

from netcdf_to_gltf_converter.geometries import Node, Triangle, TriangularMesh, Vec3
from netcdf_to_gltf_converter.gltf.builder import GLTFBuilder


def create_triangular_mesh(n: int, seed: int = 10):
    random.seed(seed)

    nodes: List[Node] = []
    for x in range(n):
        for y in range(n):
            z = random.random()
            node = Node(position=Vec3(x, y, z))
            nodes.append(node)

    triangles: List[Triangle] = []
    for node_index, node in enumerate(nodes):
        if node_index >= (n - 1) * n:
            continue

        if (node_index + 1) % n == 0:
            continue

        triangle = Triangle(node_index, node_index + n, node_index + n + 1)
        triangles.append(triangle)

        triangle = Triangle(
            node_index, triangle.node_index_3, triangle.node_index_3 - n
        )
        triangles.append(triangle)

    return TriangularMesh(nodes, triangles)


class TestGLTFBuilder:
    def test_add_triangular_mesh_produces_valid_gltf(self):
        # Create a 2x2 nodes mesh: 2 triangles
        triangular_mesh = create_triangular_mesh(n=2)

        builder = GLTFBuilder()
        builder.add_triangular_mesh(triangular_mesh)

        gltf = builder.finish()

        gltf_dict = gltf_asdict(gltf)
        exp_gltf_dict = {
            "extensions": {},
            "extras": {},
            "accessors": [
                {
                    "extensions": {},
                    "extras": {},
                    "bufferView": 0,
                    "byteOffset": 0,
                    "componentType": 5123,
                    "normalized": False,
                    "count": 6,
                    "type": "SCALAR",
                    "sparse": None,
                    "max": [3],
                    "min": [0],
                    "name": None,
                },
                {
                    "extensions": {},
                    "extras": {},
                    "bufferView": 1,
                    "byteOffset": 0,
                    "componentType": 5126,
                    "normalized": False,
                    "count": 4,
                    "type": "VEC3",
                    "sparse": None,
                    "max": [1.0, 1.0, 0.5780913233757019],
                    "min": [0.0, 0.0, 0.20609822869300842],
                    "name": None,
                },
            ],
            "animations": [],
            "asset": {
                "extensions": {},
                "extras": {},
                "generator": "pygltflib@v1.15.5",
                "copyright": None,
                "version": "2.0",
                "minVersion": None,
            },
            "bufferViews": [
                {
                    "extensions": {},
                    "extras": {},
                    "buffer": 0,
                    "byteOffset": 0,
                    "byteLength": 12,
                    "byteStride": None,
                    "target": 34963,
                    "name": None,
                },
                {
                    "extensions": {},
                    "extras": {},
                    "buffer": 0,
                    "byteOffset": 12,
                    "byteLength": 48,
                    "byteStride": None,
                    "target": 34962,
                    "name": None,
                },
            ],
            "buffers": [
                {"extensions": {}, "extras": {}, "uri": None, "byteLength": 60}
            ],
            "cameras": [],
            "extensionsUsed": [],
            "extensionsRequired": [],
            "images": [],
            "materials": [],
            "meshes": [
                {
                    "extensions": {},
                    "extras": {},
                    "primitives": [
                        {
                            "extensions": {},
                            "extras": {},
                            "attributes": {
                                "POSITION": 1,
                                "NORMAL": None,
                                "TANGENT": None,
                                "TEXCOORD_0": None,
                                "TEXCOORD_1": None,
                                "COLOR_0": None,
                                "JOINTS_0": None,
                                "WEIGHTS_0": None,
                            },
                            "indices": 0,
                            "mode": 4,
                            "material": None,
                            "targets": [],
                        }
                    ],
                    "weights": [],
                    "name": None,
                }
            ],
            "nodes": [
                {
                    "extensions": {},
                    "extras": {},
                    "mesh": 0,
                    "skin": None,
                    "rotation": None,
                    "translation": None,
                    "scale": None,
                    "children": [],
                    "matrix": None,
                    "camera": None,
                    "name": None,
                }
            ],
            "samplers": [],
            "scene": 0,
            "scenes": [{"extensions": {}, "extras": {}, "name": None, "nodes": [0]}],
            "skins": [],
            "textures": [],
        }

        assert gltf_dict == exp_gltf_dict
