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
        displacements_vertices = [
            [0, 0, random.uniform(-1, 1)] for _ in range(n_vertices)
        ]
        mesh_transformations_vertex_positions.append(displacements_vertices)

    triangles = []

    for node_index in range(len(mesh_geometry_vertex_positions)):
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
        MeshGeometry(
            vertex_positions=np.array(mesh_geometry_vertex_positions, dtype="float32")
        ),
        np.array(triangles, dtype="uint32"),
        np.array(
            [
                MeshGeometry(vertex_positions=np.array(p, dtype="float32"))
                for p in mesh_transformations_vertex_positions
            ]
        ),
    )


class TestGLTFBuilder:
    def test_add_triangular_mesh_produces_valid_gltf(self):
        # Create a mesh with 3x3 vertices with 2 time frames
        triangular_mesh = create_triangular_mesh(n_vertix_cols=5, n_frames=5)

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
                    "count": 96,
                    "type": "SCALAR",
                    "sparse": None,
                    "max": [24],
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
                    "count": 25,
                    "type": "VEC3",
                    "sparse": None,
                    "max": [4.0, 4.0, 0.9965569972991943],
                    "min": [0.0, 0.0, 0.0445563830435276],
                    "name": None,
                },
                {
                    "extensions": {},
                    "extras": {},
                    "bufferView": 2,
                    "byteOffset": 0,
                    "componentType": 5126,
                    "normalized": False,
                    "count": 25,
                    "type": "VEC4",
                    "sparse": None,
                    "max": [0.0, 0.5879999995231628, 1.0, 0.75],
                    "min": [0.0, 0.5879999995231628, 1.0, 0.75],
                    "name": None,
                },
                {
                    "extensions": {},
                    "extras": {},
                    "bufferView": 1,
                    "byteOffset": 300,
                    "componentType": 5126,
                    "normalized": False,
                    "count": 25,
                    "type": "VEC3",
                    "sparse": None,
                    "max": [0.0, 0.0, 0.9387763142585754],
                    "min": [0.0, 0.0, -0.9918897151947021],
                    "name": None,
                },
                {
                    "extensions": {},
                    "extras": {},
                    "bufferView": 1,
                    "byteOffset": 600,
                    "componentType": 5126,
                    "normalized": False,
                    "count": 25,
                    "type": "VEC3",
                    "sparse": None,
                    "max": [0.0, 0.0, 0.8953878283500671],
                    "min": [0.0, 0.0, -0.9899828433990479],
                    "name": None,
                },
                {
                    "extensions": {},
                    "extras": {},
                    "bufferView": 1,
                    "byteOffset": 900,
                    "componentType": 5126,
                    "normalized": False,
                    "count": 25,
                    "type": "VEC3",
                    "sparse": None,
                    "max": [0.0, 0.0, 0.9373564124107361],
                    "min": [0.0, 0.0, -0.8744527697563171],
                    "name": None,
                },
                {
                    "extensions": {},
                    "extras": {},
                    "bufferView": 1,
                    "byteOffset": 1200,
                    "componentType": 5126,
                    "normalized": False,
                    "count": 25,
                    "type": "VEC3",
                    "sparse": None,
                    "max": [0.0, 0.0, 0.9853761196136475],
                    "min": [0.0, 0.0, -0.9943391680717468],
                    "name": None,
                },
                {
                    "extensions": {},
                    "extras": {},
                    "bufferView": 1,
                    "byteOffset": 1500,
                    "componentType": 5126,
                    "normalized": False,
                    "count": 25,
                    "type": "VEC3",
                    "sparse": None,
                    "max": [0.0, 0.0, 0.9626387357711792],
                    "min": [0.0, 0.0, -0.9075282216072083],
                    "name": None,
                },
                {
                    "extensions": {},
                    "extras": {},
                    "bufferView": 3,
                    "byteOffset": 0,
                    "componentType": 5126,
                    "normalized": False,
                    "count": 5,
                    "type": "SCALAR",
                    "sparse": None,
                    "max": [4],
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
                    "count": 25,
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
                            "input": 8,
                            "interpolation": "LINEAR",
                            "output": 9,
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
                    "byteLength": 384,
                    "byteStride": None,
                    "target": 34963,
                    "name": None,
                },
                {
                    "extensions": {},
                    "extras": {},
                    "buffer": 0,
                    "byteOffset": 384,
                    "byteLength": 1800,
                    "byteStride": 12,
                    "target": 34962,
                    "name": None,
                },
                {
                    "extensions": {},
                    "extras": {},
                    "buffer": 1,
                    "byteOffset": 0,
                    "byteLength": 400,
                    "byteStride": None,
                    "target": None,
                    "name": None,
                },
                {
                    "extensions": {},
                    "extras": {},
                    "buffer": 2,
                    "byteOffset": 0,
                    "byteLength": 20,
                    "byteStride": None,
                    "target": None,
                    "name": None,
                },
                {
                    "extensions": {},
                    "extras": {},
                    "buffer": 2,
                    "byteOffset": 20,
                    "byteLength": 100,
                    "byteStride": None,
                    "target": None,
                    "name": None,
                },
            ],
            "buffers": [
                {
                    "extensions": {},
                    "extras": {},
                    "uri": "data:application/octet-stream;base64,AAAAAAUAAAAGAAAAAAAAAAYAAAABAAAAAQAAAAYAAAAHAAAAAQAAAAcAAAACAAAAAgAAAAcAAAAIAAAAAgAAAAgAAAADAAAAAwAAAAgAAAAJAAAAAwAAAAkAAAAEAAAABQAAAAoAAAALAAAABQAAAAsAAAAGAAAABgAAAAsAAAAMAAAABgAAAAwAAAAHAAAABwAAAAwAAAANAAAABwAAAA0AAAAIAAAACAAAAA0AAAAOAAAACAAAAA4AAAAJAAAACgAAAA8AAAAQAAAACgAAABAAAAALAAAACwAAABAAAAARAAAACwAAABEAAAAMAAAADAAAABEAAAASAAAADAAAABIAAAANAAAADQAAABIAAAATAAAADQAAABMAAAAOAAAADwAAABQAAAAVAAAADwAAABUAAAAQAAAAEAAAABUAAAAWAAAAEAAAABYAAAARAAAAEQAAABYAAAAXAAAAEQAAABcAAAASAAAAEgAAABcAAAAYAAAAEgAAABgAAAATAAAAAAAAAAAAAABxRxI/AAAAAAAAgD9Zl9s+AAAAAAAAAEDL/RM/AAAAAAAAQEBqC1M+AAAAAAAAgEDSNVA/AACAPwAAAAC41lI/AACAPwAAgD/6SSc/AACAPwAAAEA4EyQ+AACAPwAAQECWSgU/AACAPwAAgEDX0ac+AAAAQAAAAAAh/38+AAAAQAAAgD/P63M/AAAAQAAAAEBcHn8/AAAAQAAAQEDBgDY9AAAAQAAAgECEM1w/AABAQAAAAACzaho/AABAQAAAgD/cYcM+AABAQAAAAEBoNpE+AABAQAAAQEB/yiw/AABAQAAAgEDG5ek+AACAQAAAAACelC8/AACAQAAAgD/Dbik/AACAQAAAAEBsKwg+AACAQAAAQEAFkUQ/AACAQAAAgEBvf3s/AAAAAAAAAAClU3A/AAAAAAAAAADkF2g+AAAAAAAAAACsVmm/AAAAAAAAAAB87H2/AAAAAAAAAAD0Zzu/AAAAAAAAAAANy2E/AAAAAAAAAADs3sm+AAAAAAAAAAAhEYm+AAAAAAAAAABh4Es/AAAAAAAAAABqF76+AAAAAAAAAACLocg9AAAAAAAAAAA0AgO+AAAAAAAAAAAVuV6/AAAAAAAAAACSJi0+AAAAAAAAAACrKTA/AAAAAAAAAADc6S+/AAAAAAAAAACwKA2/AAAAAAAAAAAbcTK+AAAAAAAAAAAvGG2/AAAAAAAAAADWl967AAAAAAAAAACmziI/AAAAAAAAAAAqrqE+AAAAAAAAAAA+Jok9AAAAAAAAAAAL0zU/AAAAAAAAAAAUXDO/AAAAAAAAAADBsgk+AAAAAAAAAABR2IC+AAAAAAAAAADCeE8+AAAAAAAAAADqL0a/AAAAAAAAAAAAEA0/AAAAAAAAAACuiU6/AAAAAAAAAABf0iq/AAAAAAAAAAAOah0/AAAAAAAAAAAjOGU/AAAAAAAAAADsvQi+AAAAAAAAAABk9i++AAAAAAAAAAAzUAK/AAAAAAAAAAAntOa+AAAAAAAAAAA5InA+AAAAAAAAAADWoCS/AAAAAAAAAAAw00K/AAAAAAAAAABdT7W9AAAAAAAAAABGjSu/AAAAAAAAAABSS5g+AAAAAAAAAABpYSQ/AAAAAAAAAAD5FQ4/AAAAAAAAAABNvyK9AAAAAAAAAABIFpy+AAAAAAAAAAB6tgW+AAAAAAAAAACEb32/AAAAAAAAAADKrNk+AAAAAAAAAAANYqy+AAAAAAAAAAAd6bi+AAAAAAAAAAARFFe/AAAAAAAAAABPw9S9AAAAAAAAAAC4rCk+AAAAAAAAAAD0E2C+AAAAAAAAAAATNT0/AAAAAAAAAACBg7E+AAAAAAAAAAAkZgS/AAAAAAAAAADgsk89AAAAAAAAAAB9MVI/AAAAAAAAAAAWvSQ9AAAAAAAAAABbHFE+AAAAAAAAAAAj3F+/AAAAAAAAAADb5a28AAAAAAAAAADE7529AAAAAAAAAABrfEq+AAAAAAAAAADJ8iK+AAAAAAAAAABt8i0+AAAAAAAAAABXYZ49AAAAAAAAAABCjKW8AAAAAAAAAAC7HCu/AAAAAAAAAABSPvC9AAAAAAAAAACX9m8/AAAAAAAAAABquS2+AAAAAAAAAADS6m2/AAAAAAAAAAADjX6/AAAAAAAAAADwEpE9AAAAAAAAAABOG2a/AAAAAAAAAADwg1C/AAAAAAAAAAAUUUi/AAAAAAAAAABcGLy9AAAAAAAAAACcQXw/AAAAAAAAAABn2vS8AAAAAAAAAADOaKm9AAAAAAAAAACeBgK+AAAAAAAAAAC7xhE7AAAAAAAAAADPuti9AAAAAAAAAAD1pOc+AAAAAAAAAAD+vks/AAAAAAAAAACGnso+AAAAAAAAAABVDx2+AAAAAAAAAAApHpk+AAAAAAAAAABOr1E/AAAAAAAAAADCVzG/AAAAAAAAAAANewa/AAAAAAAAAAD+8HM+AAAAAAAAAAAogr8+AAAAAAAAAADLBZI+AAAAAAAAAAB3TjU+AAAAAAAAAAAoqig/AAAAAAAAAADUfyy9AAAAAAAAAABKfB0/AAAAAAAAAADouWw/AAAAAAAAAAC3YwS+AAAAAAAAAACcujc/AAAAAAAAAADuet8+AAAAAAAAAABDAUc/AAAAAAAAAADFU2i/AAAAAAAAAACqgVM/AAAAAAAAAAAPnwg/AAAAAAAAAADuvGw/AAAAAAAAAAB+b3Y/AAAAAAAAAAChqdu+AAAAAAAAAADTFK4+AAAAAAAAAAD/qje/AAAAAAAAAAD31EI+AAAAAAAAAAAm01Y/AAAAAAAAAACstR2/AAAAAAAAAAAGvJm+AAAAAAAAAACTK1e/AAAAAAAAAAACVhy/AAAAAAAAAAD/pxW/AAAAAAAAAAD32E6/",
                    "byteLength": 2184,
                },
                {
                    "extensions": {},
                    "extras": {},
                    "uri": "data:application/octet-stream;base64,AAAAACuHFj8AAIA/AABAPwAAAAArhxY/AACAPwAAQD8AAAAAK4cWPwAAgD8AAEA/AAAAACuHFj8AAIA/AABAPwAAAAArhxY/AACAPwAAQD8AAAAAK4cWPwAAgD8AAEA/AAAAACuHFj8AAIA/AABAPwAAAAArhxY/AACAPwAAQD8AAAAAK4cWPwAAgD8AAEA/AAAAACuHFj8AAIA/AABAPwAAAAArhxY/AACAPwAAQD8AAAAAK4cWPwAAgD8AAEA/AAAAACuHFj8AAIA/AABAPwAAAAArhxY/AACAPwAAQD8AAAAAK4cWPwAAgD8AAEA/AAAAACuHFj8AAIA/AABAPwAAAAArhxY/AACAPwAAQD8AAAAAK4cWPwAAgD8AAEA/AAAAACuHFj8AAIA/AABAPwAAAAArhxY/AACAPwAAQD8AAAAAK4cWPwAAgD8AAEA/AAAAACuHFj8AAIA/AABAPwAAAAArhxY/AACAPwAAQD8AAAAAK4cWPwAAgD8AAEA/AAAAACuHFj8AAIA/AABAPw==",
                    "byteLength": 400,
                },
                {
                    "extensions": {},
                    "extras": {},
                    "uri": "data:application/octet-stream;base64,AAAAAAAAgD8AAABAAABAQAAAgEAAAIA/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAIA/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAIA/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAIA/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAIA/",
                    "byteLength": 120,
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
                                "COLOR_0": 2,
                                "JOINTS_0": None,
                                "WEIGHTS_0": None,
                            },
                            "indices": 0,
                            "mode": 4,
                            "material": None,
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
                                {
                                    "POSITION": 5,
                                    "NORMAL": None,
                                    "TANGENT": None,
                                    "TEXCOORD_0": None,
                                    "TEXCOORD_1": None,
                                    "COLOR_0": None,
                                    "JOINTS_0": None,
                                    "WEIGHTS_0": None,
                                },
                                {
                                    "POSITION": 6,
                                    "NORMAL": None,
                                    "TANGENT": None,
                                    "TEXCOORD_0": None,
                                    "TEXCOORD_1": None,
                                    "COLOR_0": None,
                                    "JOINTS_0": None,
                                    "WEIGHTS_0": None,
                                },
                                {
                                    "POSITION": 7,
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
                    "weights": [0.0, 0.0, 0.0, 0.0, 0.0],
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
