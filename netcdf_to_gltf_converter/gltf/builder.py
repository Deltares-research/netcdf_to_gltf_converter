from typing import Any, List

from pygltflib import (
    ARRAY_BUFFER,
    ELEMENT_ARRAY_BUFFER,
    FLOAT,
    GLTF2,
    SCALAR,
    UNSIGNED_INT,
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


def add(list: List[Any], item: Any) -> int:
    list.append(item)
    return len(list) - 1


class GLTFBuilder:
    def __init__(self) -> None:
        """Initialize a GLTFBuilder.

        Assumption: the GLTF will contain only one scene.
        """

        # Create GLTF root object
        self._gltf = GLTF2()

        # Add single scene to the gltf scenes
        scene = Scene()
        scene_index = add(self._gltf.scenes, scene)

        # Set only scene as default scene
        self._gltf.scene = scene_index
        self._scene = scene

        # Add mesh to gltf meshes
        mesh = Mesh()
        self._mesh_index = add(self._gltf.meshes, mesh)

        # Add node to gltf nodes
        node = Node(mesh=self._mesh_index)
        node_index = add(self._gltf.nodes, node)

        # Add node index to scene
        add(self._scene.nodes, node_index)

        self._binary_blob = b""

    def add_triangular_mesh(self, triangular_mesh: TriangularMesh):
        """Add a new mesh given the triangular mesh geometry.

        Args:
            triangular_mesh (TriangularMesh): The triangular mesh.
        """

        # Prepare data
        triangles = triangular_mesh.triangles_as_array()
        triangles_binary_blob = triangles.flatten().tobytes()
        nodes = triangular_mesh.nodes_positions_as_array()
        nodes_binary_blob = nodes.tobytes()

        # Add a buffer to the gltf buffers
        geometry_bufer = Buffer()
        geometry_bufer_index = add(self._gltf.buffers, geometry_bufer)

        # Add a buffer view for the indices to the gltf buffer views
        byte_length = len(triangles_binary_blob)
        indices_buffer_view = BufferView(
            buffer=geometry_bufer_index,
            byteOffset=0,
            byteLength=byte_length,
            target=ELEMENT_ARRAY_BUFFER,
        )
        indices_buffer_view_index = add(self._gltf.bufferViews, indices_buffer_view)
        self._binary_blob += triangles_binary_blob

        # Add an accessor for the indices to the gltf accessors
        indices_accessor = Accessor(
            bufferView=indices_buffer_view_index,
            componentType=UNSIGNED_INT,
            count=triangles.size,
            type=SCALAR,
            max=[int(triangles.max())],
            min=[int(triangles.min())],
        )
        indices_accessor_index = add(self._gltf.accessors, indices_accessor)

        # Add a buffer view for the vertices to the gltf buffer views
        byte_offset = indices_buffer_view.byteOffset + indices_buffer_view.byteLength
        n_padding_bytes = byte_offset % 4
        if n_padding_bytes != 0:
            byte_offset += n_padding_bytes
            self._binary_blob += n_padding_bytes * PADDING_BYTE

        byte_length = len(nodes_binary_blob)

        positions_buffer_view = BufferView(
            buffer=geometry_bufer_index,
            byteOffset=byte_offset,
            byteLength=byte_length,
            target=ARRAY_BUFFER,
        )
        positions_buffer_view_index = add(self._gltf.bufferViews, positions_buffer_view)
        self._binary_blob += nodes_binary_blob

        # Add an accessor for the vertices to the gltf accessors
        max_xyz = nodes.max(axis=0).tolist()
        min_xyz = nodes.min(axis=0).tolist()

        positions_accessor = Accessor(
            bufferView=positions_buffer_view_index,
            componentType=FLOAT,
            count=len(nodes),
            type=VEC3,
            max=max_xyz,
            min=min_xyz,
        )
        positions_accessor_index = add(self._gltf.accessors, positions_accessor)

        # After all buffer views are added, set the total byte length of the buffer
        geometry_bufer.byteLength = positions_buffer_view.byteOffset + positions_buffer_view.byteLength

        # Add primitive to mesh primitives
        primitive = Primitive(
            attributes=Attributes(POSITION=positions_accessor_index),
            indices=indices_accessor_index,
        )
        add(self._gltf.meshes[self._mesh_index].primitives, primitive)

        self._gltf.set_binary_blob(self._binary_blob)

    def finish(self) -> GLTF2:
        """Finish the GLTF build and return the results

        Returns:
            GLTF2: The created GLTF2 object.
        """
        return self._gltf
