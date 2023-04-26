import random
from typing import List

from pygltflib import gltf_asdict

from netcdf_to_gltf_converter.geometries import Node, Triangle, TriangularMesh, Vec3
from netcdf_to_gltf_converter.gltf.builder import GLTFBuilder


def create_triangular_mesh(n: int, seed: int = 10):
    random.seed(seed)

    nodes_transformation1: List[Node] = []
    nodes_transformation2: List[Node] = []

    nodes: List[Node] = []
    for x in range(n):
        for y in range(n):
            nodes.append(Node(position=Vec3(x, y, random.random())))
            nodes_transformation1.append(Node(position=Vec3(0, 0, random.random())))
            nodes_transformation2.append(Node(position=Vec3(0, 0, random.random())))

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

    return TriangularMesh(
        nodes, triangles, [nodes_transformation1, nodes_transformation2]
    )


class TestGLTFBuilder:
    def test_add_triangular_mesh_produces_valid_gltf(self):
        # Create a 2x2 nodes mesh: 2 triangles
        triangular_mesh = create_triangular_mesh(n=2)

        builder = GLTFBuilder()
        builder.add_triangular_mesh(triangular_mesh)

        gltf = builder.finish()

        gltf.save("testietest.gltf")

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
                    "componentType": 5125,
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
                    "max": [1.0, 1.0, 0.6534725427627563],
                    "min": [0.0, 0.0, 0.20609822869300842],
                    "name": None,
                },
                {
                    "extensions": {},
                    "extras": {},
                    "bufferView": 1,
                    "byteOffset": 48,
                    "componentType": 5126,
                    "normalized": False,
                    "count": 4,
                    "type": "VEC3",
                    "sparse": None,
                    "max": [0.0, 0.0, 0.8133212327957153],
                    "min": [0.0, 0.0, 0.16022956371307373],
                    "name": None,
                },
                {
                    "extensions": {},
                    "extras": {},
                    "bufferView": 1,
                    "byteOffset": 96,
                    "componentType": 5126,
                    "normalized": False,
                    "count": 4,
                    "type": "VEC3",
                    "sparse": None,
                    "max": [0.0, 0.0, 0.952816903591156],
                    "min": [0.0, 0.0, 0.5206693410873413],
                    "name": None,
                },
                {
                    "extensions": {},
                    "extras": {},
                    "bufferView": 2,
                    "byteOffset": 0,
                    "componentType": 5126,
                    "normalized": False,
                    "count": 2,
                    "type": "SCALAR",
                    "sparse": None,
                    "max": [1],
                    "min": [0],
                    "name": None,
                },
                {
                    "extensions": {},
                    "extras": {},
                    "bufferView": 3,
                    "byteOffset": 0,
                    "componentType": 5126,
                    "normalized": False,
                    "count": 4,
                    "type": "SCALAR",
                    "sparse": None,
                    "max": [1],
                    "min": [0],
                    "name": None,
                },
            ],
            "animations": [
                {
                    "extensions": {},
                    "extras": {},
                    "name": None,
                    "channels": [
                        {
                            "extensions": {},
                            "extras": {},
                            "sampler": 0,
                            "target": {
                                "extensions": {},
                                "extras": {},
                                "node": 0,
                                "path": "weights",
                            },
                        }
                    ],
                    "samplers": [
                        {
                            "extensions": {},
                            "extras": {},
                            "input": 4,
                            "interpolation": "LINEAR",
                            "output": 5,
                        }
                    ],
                }
            ],
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
                    "byteLength": 24,
                    "byteStride": None,
                    "target": 34963,
                    "name": None,
                },
                {
                    "extensions": {},
                    "extras": {},
                    "buffer": 0,
                    "byteOffset": 24,
                    "byteLength": 144,
                    "byteStride": 12,
                    "target": 34962,
                    "name": None,
                },
                {
                    "extensions": {},
                    "extras": {},
                    "buffer": 1,
                    "byteOffset": 0,
                    "byteLength": 8,
                    "byteStride": None,
                    "target": None,
                    "name": None,
                },
                {
                    "extensions": {},
                    "extras": {},
                    "buffer": 1,
                    "byteOffset": 8,
                    "byteLength": 16,
                    "byteStride": None,
                    "target": None,
                    "name": None,
                },
            ],
            "buffers": [
                {
                    "extensions": {},
                    "extras": {},
                    "uri": "data:application/octet-stream;base64,AAAAAAIAAAADAAAAAAAAAAMAAAABAAAAAAAAAAAAAABxRxI/AAAAAAAAgD9qC1M+AACAPwAAAAD6SSc/AACAPwAAgD/X0ac+AAAAAAAAAABZl9s+AAAAAAAAAADSNVA/AAAAAAAAAAA4EyQ+AAAAAAAAAAAh/38+AAAAAAAAAADL/RM/AAAAAAAAAAC41lI/AAAAAAAAAACWSgU/AAAAAAAAAADP63M/",
                    "byteLength": 168,
                },
                {
                    "extensions": {},
                    "extras": {},
                    "uri": "data:application/octet-stream;base64,AAAAAAAAgD8AAIA/AAAAAAAAAAAAAIA/",
                    "byteLength": 24,
                },
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
                            "targets": [
                                {
                                    "POSITION": 2,
                                    "NORMAL": None,
                                    "TANGENT": None,
                                    "TEXCOORD_0": None,
                                    "TEXCOORD_1": None,
                                    "COLOR_0": None,
                                    "JOINTS_0": None,
                                    "WEIGHTS_0": None,
                                },
                                {
                                    "POSITION": 3,
                                    "NORMAL": None,
                                    "TANGENT": None,
                                    "TEXCOORD_0": None,
                                    "TEXCOORD_1": None,
                                    "COLOR_0": None,
                                    "JOINTS_0": None,
                                    "WEIGHTS_0": None,
                                },
                            ],
                        }
                    ],
                    "weights": [0.0, 0.0],
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
