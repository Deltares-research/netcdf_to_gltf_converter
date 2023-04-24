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
        self._scene = Scene()
        self._gltf.scenes.append(self._scene)
        scene_index = self._gltf.scenes.index(self._scene)

        # Set only scene as default scene
        self._gltf.scene = scene_index

        # Add mesh to gltf meshes
        self._mesh = Mesh()
        self._gltf.meshes.append(self._mesh)
        self._mesh_index = self._gltf.meshes.index(self._mesh)

        # Add node to gltf nodes
        self._node = Node(mesh=self._mesh_index)
        self._gltf.nodes.append(self._node)
        self._node_index = self._gltf.nodes.index(self._node)

        # Add node index to scene
        self._scene.nodes.append(self._node_index)
        
        # Add a geometry buffer for the mesh to the scene
        self._geometry_buffer = Buffer()
        self._gltf.buffers.append(self._geometry_buffer)

        # Add a buffer view for the indices
        self._indices_buffer_view = BufferView(
            buffer=self._gltf.buffers.index(self._geometry_buffer),
            byteOffset=0,
            target=ELEMENT_ARRAY_BUFFER,
        )
        self._gltf.bufferViews.append(self._indices_buffer_view)
        
        # Add buffer view for the vertex positions
        self._positions_buffer_view = BufferView(
            buffer=self._gltf.buffers.index(self._geometry_buffer),
            target=ARRAY_BUFFER,
        )
        self._gltf.bufferViews.append(self._positions_buffer_view)
        
        self._vertices_buffer_view = BufferView()
        
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
        
        # Add a buffer view for the indices to the gltf buffer views
        byte_length = len(triangles_binary_blob)
        self._indices_buffer_view.byteLength = byte_length
        self._binary_blob += triangles_binary_blob

        # Add an accessor for the indices to the gltf accessors
        indices_accessor = Accessor(
            bufferView=self._gltf.bufferViews.index(self._indices_buffer_view),
            componentType=UNSIGNED_INT,
            count=triangles.size,
            type=SCALAR,
            max=[int(triangles.max())],
            min=[int(triangles.min())],
        )
        indices_accessor_index = add(self._gltf.accessors, indices_accessor)

        # Add a buffer view for the vertices to the gltf buffer views
        byte_offset = self._indices_buffer_view.byteOffset + self._indices_buffer_view.byteLength
        n_padding_bytes = byte_offset % 4
        if n_padding_bytes != 0:
            byte_offset += n_padding_bytes
            self._binary_blob += n_padding_bytes * PADDING_BYTE

        byte_length = len(nodes_binary_blob)

        self._positions_buffer_view.byteOffset = byte_offset
        self._positions_buffer_view.byteLength = byte_length

        self._binary_blob += nodes_binary_blob

        # Add an accessor for the vertices to the gltf accessors
        max_xyz = nodes.max(axis=0).tolist()
        min_xyz = nodes.min(axis=0).tolist()

        positions_accessor = Accessor(
            bufferView=self._gltf.bufferViews.index(self._positions_buffer_view),
            componentType=FLOAT,
            count=len(nodes),
            type=VEC3,
            max=max_xyz,
            min=min_xyz,
        )
        positions_accessor_index = add(self._gltf.accessors, positions_accessor)

        # After all buffer views are added, set the total byte length of the buffer
        self._geometry_buffer.byteLength = self._positions_buffer_view.byteOffset + self._positions_buffer_view.byteLength

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
