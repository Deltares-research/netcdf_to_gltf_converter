import random
import numpy as np

from pygltflib import gltf_asdict

from netcdf_to_gltf_converter.geometries import MeshGeometry, TriangularMesh
from netcdf_to_gltf_converter.gltf.builder import GLTFBuilder


def create_triangular_mesh(n_vertix_cols: int, n_frames: int, seed: int = 10):
    random.seed(seed)

    mesh_geometry_vertex_positions = []
    mesh_transformations_vertex_positions = []

    for x in range(n_vertix_cols):
        for y in range(n_vertix_cols):
            mesh_geometry_vertex_positions.append([x, y, random.random()])
            
    n_vertices = n_vertix_cols * n_vertix_cols
    for _ in range(n_frames):
        displacements_vertices = [[0, 0, random.uniform(-1, 1)] for _ in range(n_vertices)]
        mesh_transformations_vertex_positions.append(displacements_vertices)
        
    triangles = []

    for node_index in range(len(mesh_geometry_vertex_positions)):
        if node_index >= (n_vertix_cols - 1) * n_vertix_cols:
            continue

        if (node_index + 1) % n_vertix_cols == 0:
            continue

        triangle1 = [node_index, node_index + n_vertix_cols, node_index + n_vertix_cols + 1]
        triangles.append(triangle1)

        triangle2 = [node_index, triangle1[2], triangle1[2] - n_vertix_cols]
        triangles.append(triangle2)

    return TriangularMesh(
        MeshGeometry(vertex_positions=np.array(mesh_geometry_vertex_positions, dtype="float32")), 
        np.array(triangles, dtype="uint32"), 
        np.array([MeshGeometry(vertex_positions=np.array(p, dtype="float32")) for p in mesh_transformations_vertex_positions])
    )


class TestGLTFBuilder:
    def test_add_triangular_mesh_produces_valid_gltf(self):
        # Create a 2x2 nodes mesh: 2 triangles
        triangular_mesh = create_triangular_mesh(n_vertix_cols=5, n_frames=5)

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

        #assert gltf_dict == exp_gltf_dict
