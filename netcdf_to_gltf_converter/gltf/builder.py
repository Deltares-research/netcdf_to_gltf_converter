from typing import Any, List

import numpy as np
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
        self._geometry_buffer = Buffer(byteLength=0)
        self._gltf.buffers.append(self._geometry_buffer)

        # Add a buffer view for the indices
        self._indices_buffer_view = BufferView(
            buffer=self._gltf.buffers.index(self._geometry_buffer),
            byteOffset=0,
            byteLength=0,
            target=ELEMENT_ARRAY_BUFFER,
        )
        self._gltf.bufferViews.append(self._indices_buffer_view)

        # Add buffer view for the vertex positions
        self._positions_buffer_view = BufferView(
            buffer=self._gltf.buffers.index(self._geometry_buffer),
            byteOffset=0,
            byteLength=0,
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

        triangles = triangular_mesh.triangles_as_array()
        nodes = triangular_mesh.nodes_positions_as_array()

        indices_accessor_index = self._add_accessor_to_bufferview(triangles, self._indices_buffer_view, UNSIGNED_INT, SCALAR)
        positions_accessor_index = self._add_accessor_to_bufferview(nodes, self._positions_buffer_view, FLOAT, VEC3)

        primitive = Primitive(
            attributes=Attributes(POSITION=positions_accessor_index),
            indices=indices_accessor_index,
        )
        self._gltf.meshes[self._mesh_index].primitives.append(primitive)
        
        # for each time step time_i:
        #   add new position accessor to positions buffer view
        #   add new target to primitive that points to each accessor
        #

        self._gltf.set_binary_blob(self._binary_blob)

    def _add_accessor_to_bufferview(
        self, data: np.ndarray, buffer_view: BufferView, component_type: int, type: str
    ) -> int:

        buffer = self._gltf.buffers[buffer_view.buffer]
        
        if buffer_view.byteLength == 0: # offset has not been determined yet
            buffer_view_byte_offset = buffer.byteLength # offset should start after existing data in buffer
            n_padding_bytes = buffer_view_byte_offset % 4 # add padding bytes between bufferviews if needed, TODO number of bytes should be according to accessor componenttype, 
            if n_padding_bytes != 0:
                buffer_view_byte_offset += n_padding_bytes # buffer view should start after the padding bytes
                buffer.byteLength += n_padding_bytes # at to total length of buffer 
                self._binary_blob += n_padding_bytes * PADDING_BYTE # add to total binary data?? 

            buffer_view.byteOffset = buffer_view_byte_offset ## set offset
        
        data_binary_blob = data.flatten().tobytes()
        accessor_byte_length = len(data_binary_blob)
        
        accessor_byte_offset = buffer_view.byteLength # accessor should start after existing data in bufferview
        
        buffer.byteLength += accessor_byte_length # add bytes to total length buffer
        buffer_view.byteLength += accessor_byte_length # add bytes to total  length of bufferview

        self._binary_blob += data_binary_blob
        
        max, min, count = self._get_min_max_count(data, type)
        accessor = Accessor(
            bufferView=self._gltf.bufferViews.index(buffer_view),
            byteOffset=accessor_byte_offset, 
            componentType=component_type,
            count=count,
            type=type,
            max=max,
            min=min,
        )
        self._gltf.accessors.append(accessor)
        
        return self._gltf.accessors.index(accessor)

    def _get_min_max_count(self, data: np.ndarray, type: str):
        if type == SCALAR:
            max = [int(data.max())]
            min = [int(data.min())]
            count = data.size
        elif type == VEC3:
            max = data.max(axis=0).tolist()
            min = data.min(axis=0).tolist()
            count = len(data)
        else:
            raise ValueError(f"Type {type} not supported.")
        
        return max, min, count
        
    def finish(self) -> GLTF2:
        """Finish the GLTF build and return the results

        Returns:
            GLTF2: The created GLTF2 object.
        """
        return self._gltf
