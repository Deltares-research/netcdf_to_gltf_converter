import numpy as np
from pygltflib import (
    ARRAY_BUFFER,
    ELEMENT_ARRAY_BUFFER,
    FLOAT,
    GLTF2,
    SCALAR,
    UNSIGNED_BYTE,
    VEC3,
    Accessor,
    Attributes,
    Buffer,
    BufferView,
    Mesh,
    Node,
    Primitive,
    Scene,
)

from netcdf_to_gltf_converter.geometries import TriangularMesh

PADDING_BYTE = b"\x00"


class GLTFBuilder:
    def __init__(self) -> None:
        """Initialize a GLTFBuilder.

        Assumption: the GLTF will contain only one scene.
        """

        self._gltf = GLTF2()
        self._gltf.scene = 0
        self._scene = Scene()
        self._gltf.scenes.append(self._scene)

        self._binary_blob = b""

    def add_triangular_mesh(self, triangular_mesh: TriangularMesh):
        """Add a new mesh given the triangular mesh geometry.

        Args:
            triangular_mesh (TriangularMesh): The triangular mesh.
        """

        self._add_mesh()

        triangles = triangular_mesh.triangles_as_array()
        nodes = triangular_mesh.nodes_positions_as_array()

        self._add_index_accessor(triangles)
        self._add_position_accessor(nodes)

        triangles_binary_blob = triangles.flatten().tobytes()
        nodes_binary_blob = nodes.tobytes()

        buffer_index = len(self._gltf.buffers)

        self._add_buffer()
        self._add_buffer_view(
            triangles_binary_blob, buffer_index, target=ELEMENT_ARRAY_BUFFER
        )
        self._add_buffer_view(nodes_binary_blob, buffer_index, target=ARRAY_BUFFER)

        self._gltf.set_binary_blob(self._binary_blob)

    def _add_mesh(self):
        # Add node index to scene
        node_index = len(self._gltf.nodes)
        self._scene.nodes.append(node_index)

        # Add node to gltf nodes
        mesh_index = len(self._gltf.meshes)
        node = Node(mesh=mesh_index)
        self._gltf.nodes.append(node)

        # Add mesh to gltf meshes
        mesh = Mesh()
        self._gltf.meshes.append(mesh)

        # Add primitive to mesh primitives
        indices_accessor_index = len(self._gltf.accessors)
        position_accessor_index = indices_accessor_index + 1
        primitive = Primitive(
            attributes=Attributes(POSITION=position_accessor_index),
            indices=indices_accessor_index,
        )
        mesh.primitives.append(primitive)

    def _add_index_accessor(self, triangles: np.ndarray):
        accessor = Accessor(
            bufferView=0,
            componentType=UNSIGNED_BYTE,
            count=triangles.size,
            type=SCALAR,
            max=[int(triangles.max())],
            min=[int(triangles.min())],
        )
        self._gltf.accessors.append(accessor)

    def _add_position_accessor(self, nodes: np.ndarray):
        max_xyz = nodes.max(axis=0).tolist()
        min_xyz = nodes.min(axis=0).tolist()

        accessor = Accessor(
            bufferView=1,
            componentType=FLOAT,
            count=len(nodes),
            type=VEC3,
            max=max_xyz,
            min=min_xyz,
        )
        self._gltf.accessors.append(accessor)

    def _add_buffer(self):
        buffer = Buffer(byteLength=0)
        self._gltf.buffers.append(buffer)

    def _add_buffer_view(self, blob: bytes, buffer_index: int, target: int):
        if len(self._gltf.bufferViews) == 0:
            byte_offset = 0
        else:
            previous_buffer_view = self._gltf.bufferViews[-1]
            byte_offset = (
                previous_buffer_view.byteOffset + previous_buffer_view.byteLength
            )
            n_padding_bytes = byte_offset % 4
            if n_padding_bytes != 0:
                byte_offset += n_padding_bytes
                self._binary_blob += n_padding_bytes * PADDING_BYTE

        byte_length = len(blob)

        buffer_view = BufferView(
            buffer=buffer_index,
            byteOffset=byte_offset,
            byteLength=byte_length,
            target=target,
        )

        self._gltf.bufferViews.append(buffer_view)
        self._gltf.buffers[buffer_index].byteLength = byte_offset + byte_length
        self._binary_blob += blob
