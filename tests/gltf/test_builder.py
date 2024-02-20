import random

from pygltflib import gltf_asdict

from netcdf_to_gltf_converter.data.mesh import MeshAttributes, TriangularMesh
from netcdf_to_gltf_converter.gltf.builder import GLTFBuilder
from netcdf_to_gltf_converter.utils.arrays import float32_array, uint32_array


def create_triangular_mesh(n_vertix_cols: int, n_frames: int, seed: int = 10):
    random.seed(seed)

    base_geometry_vertex_positions = []
    transformations_vertex_positions = []

    for x in range(n_vertix_cols):
        for y in range(n_vertix_cols):
            base_geometry_vertex_positions.append([x, y, random.random()])

    n_vertices = n_vertix_cols * n_vertix_cols
    for _ in range(n_frames):
        displacements_vertices = [
            [0, 0, random.uniform(-1, 1)] for _ in range(n_vertices)
        ]
        transformations_vertex_positions.append(displacements_vertices)

    triangles = []

    for node_index in range(len(base_geometry_vertex_positions)):
        if node_index >= (n_vertix_cols - 1) * n_vertix_cols:
            continue

        if (node_index + 1) % n_vertix_cols == 0:
            continue

        triangle1 = [
            node_index,
            node_index + n_vertix_cols,
            node_index + n_vertix_cols + 1,
        ]
        triangles.append(triangle1)

        triangle2 = [node_index, triangle1[2], triangle1[2] - n_vertix_cols]
        triangles.append(triangle2)

    return TriangularMesh(
        MeshAttributes(
            vertex_positions=float32_array(base_geometry_vertex_positions),
            mesh_color=[0.38, 0.73, 0.78, 1.0],
        ),
        uint32_array(triangles),
        [
            MeshAttributes(
                vertex_positions=float32_array(p), mesh_color=[0.38, 0.73, 0.78, 1.0]
            )
            for p in transformations_vertex_positions
        ],
        metallic_factor=0.0,
        roughness_factor=0.1,
    )


class TestGLTFBuilder:
    def test_add_triangular_mesh_produces_valid_gltf(self):
        # Create a mesh with 3x3 vertices with 2 time frames
        triangular_mesh = create_triangular_mesh(n_vertix_cols=3, n_frames=2)

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
                    "componentType": 5125,
                    "normalized": False,
                    "count": 24,
                    "type": "SCALAR",
                    "sparse": None,
                    "max": [8],
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
                    "count": 9,
                    "type": "VEC3",
                    "sparse": None,
                    "max": [2.0, 2.0, 0.8235888481140137],
                    "min": [0.0, 0.0, 0.16022956371307373],
                    "name": None,
                },
                {
                    "extensions": {},
                    "extras": {},
                    "bufferView": 2,
                    "byteOffset": 0,
                    "componentType": 5126,
                    "normalized": False,
                    "count": 9,
                    "type": "VEC4",
                    "sparse": None,
                    "max": [
                        0.3799999952316284,
                        0.7300000190734863,
                        0.7799999713897705,
                        1.0,
                    ],
                    "min": [
                        0.3799999952316284,
                        0.7300000190734863,
                        0.7799999713897705,
                        1.0,
                    ],
                    "name": None,
                },
                {
                    "extensions": {},
                    "extras": {},
                    "bufferView": 1,
                    "byteOffset": 108,
                    "componentType": 5126,
                    "normalized": False,
                    "count": 9,
                    "type": "VEC3",
                    "sparse": None,
                    "max": [0.0, 0.0, 0.9931139945983887],
                    "min": [0.0, 0.0, -0.9108872413635254],
                    "name": None,
                },
                {
                    "extensions": {},
                    "extras": {},
                    "bufferView": 1,
                    "byteOffset": 216,
                    "componentType": 5126,
                    "normalized": False,
                    "count": 9,
                    "type": "VEC3",
                    "sparse": None,
                    "max": [0.0, 0.0, 0.9648265242576599],
                    "min": [0.0, 0.0, -0.7340437173843384],
                    "name": None,
                },
                {
                    "extensions": {},
                    "extras": {},
                    "bufferView": 3,
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
                    "bufferView": 4,
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
                            "input": 5,
                            "interpolation": "LINEAR",
                            "output": 6,
                        }
                    ],
                }
            ],
            "asset": {
                "extensions": {},
                "extras": {},
                "generator": "pygltflib@v1.16.1",
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
                    "byteLength": 96,
                    "byteStride": None,
                    "target": 34963,
                    "name": None,
                },
                {
                    "extensions": {},
                    "extras": {},
                    "buffer": 0,
                    "byteOffset": 96,
                    "byteLength": 324,
                    "byteStride": 12,
                    "target": 34962,
                    "name": None,
                },
                {
                    "extensions": {},
                    "extras": {},
                    "buffer": 1,
                    "byteOffset": 0,
                    "byteLength": 144,
                    "byteStride": None,
                    "target": None,
                    "name": None,
                },
                {
                    "extensions": {},
                    "extras": {},
                    "buffer": 2,
                    "byteOffset": 0,
                    "byteLength": 8,
                    "byteStride": None,
                    "target": None,
                    "name": None,
                },
                {
                    "extensions": {},
                    "extras": {},
                    "buffer": 2,
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
                    "uri": "data:application/octet-stream;base64,AAAAAAMAAAAEAAAAAAAAAAQAAAABAAAAAQAAAAQAAAAFAAAAAQAAAAUAAAACAAAAAwAAAAYAAAAHAAAAAwAAAAcAAAAEAAAABAAAAAcAAAAIAAAABAAAAAgAAAAFAAAAAAAAAAAAAABxRxI/AAAAAAAAgD9Zl9s+AAAAAAAAAEDL/RM/AACAPwAAAABqC1M+AACAPwAAgD/SNVA/AACAPwAAAEC41lI/AAAAQAAAAAD6SSc/AAAAQAAAgD84EyQ+AAAAQAAAAECWSgU/AAAAAAAAAABTXLC+AAAAAAAAAABwAAC/AAAAAAAAAACe12c/AAAAAAAAAAC4PH4/AAAAAAAAAADoL2m/AAAAAAAAAAAHZzg/AAAAAAAAAACZVVM+AAAAAAAAAACQeHK+AAAAAAAAAAAwk92+AAAAAAAAAAD8KbM+AAAAAAAAAADS0bC9AAAAAAAAAAB5Ur4+AAAAAAAAAAALu6U+AAAAAAAAAABK6ju/AAAAAAAAAAAKIgk/AAAAAAAAAADf/nY/AAAAAAAAAAClU3A/AAAAAAAAAADkF2g+",
                    "byteLength": 420,
                },
                {
                    "extensions": {},
                    "extras": {},
                    "uri": "data:application/octet-stream;base64,XI/CPkjhOj8Urkc/AACAP1yPwj5I4To/FK5HPwAAgD9cj8I+SOE6PxSuRz8AAIA/XI/CPkjhOj8Urkc/AACAP1yPwj5I4To/FK5HPwAAgD9cj8I+SOE6PxSuRz8AAIA/XI/CPkjhOj8Urkc/AACAP1yPwj5I4To/FK5HPwAAgD9cj8I+SOE6PxSuRz8AAIA/",
                    "byteLength": 144,
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
            "materials": [
                {
                    "extensions": {},
                    "extras": {},
                    "pbrMetallicRoughness": {
                        "extensions": {},
                        "extras": {},
                        "baseColorFactor": [1.0, 1.0, 1.0, 1.0],
                        "metallicFactor": 0.0,
                        "roughnessFactor": 0.1,
                        "baseColorTexture": None,
                        "metallicRoughnessTexture": None,
                    },
                    "normalTexture": None,
                    "occlusionTexture": None,
                    "emissiveFactor": [0.0, 0.0, 0.0],
                    "emissiveTexture": None,
                    "alphaMode": "OPAQUE",
                    "alphaCutoff": 0.5,
                    "doubleSided": False,
                    "name": None,
                }
            ],
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
                                "COLOR_0": 2,
                                "JOINTS_0": None,
                                "WEIGHTS_0": None,
                            },
                            "indices": 0,
                            "mode": 4,
                            "material": 0,
                            "targets": [
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
                                {
                                    "POSITION": 4,
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
