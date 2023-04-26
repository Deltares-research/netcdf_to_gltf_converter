from typing import Any, List

import numpy as np
from pygltflib import (
    ANIM_LINEAR,
    Animation,
    AnimationChannel,
    AnimationChannelTarget,
    AnimationSampler,
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

class BufferWrapper:
    def __init__(self, buffer: Buffer) -> None:
        self.buffer = buffer
        self.binary_blob = b""

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

        self._buffer_wrappers: List[BufferWrapper] = []
        # Add a geometry buffer for the mesh
        self._geometry_buffer = self.add_buffer(Buffer(byteLength=0, uri="geometry.bin"))

        # Add a buffer view for the indices
        self._indices_buffer_view = BufferView(
            buffer=self._buffer_wrappers.index(self._geometry_buffer),
            byteOffset=0,
            byteLength=0,
            target=ELEMENT_ARRAY_BUFFER,
        )
        self._gltf.bufferViews.append(self._indices_buffer_view)

        # Add buffer view for the vertex positions
        self._positions_buffer_view = BufferView(
            buffer=self._buffer_wrappers.index(self._geometry_buffer),
            byteOffset=0,
            byteLength=0,
            target=ARRAY_BUFFER,
        )
        self._gltf.bufferViews.append(self._positions_buffer_view)
        
        # Add a animation buffer for the mesh
        self._animation_buffer = self.add_buffer(Buffer(byteLength=0, uri="animation.bin"))
        
        # Add buffer view for the sampler inputs
        self._sampler_inputs_buffer_view = BufferView(
            buffer=self._buffer_wrappers.index(self._animation_buffer),
            #buffer=1,
            byteOffset=0,
            byteLength=0
        )
        self._gltf.bufferViews.append(self._sampler_inputs_buffer_view)
        
        # Add buffer view for the sampler outputs
        self._sampler_outputs_buffer_view = BufferView(
            buffer=self._buffer_wrappers.index(self._animation_buffer),
            #buffer=1,
            byteOffset=0,
            byteLength=0
        )
        self._gltf.bufferViews.append(self._sampler_outputs_buffer_view)

        self._binary_blob = b""
        
    def add_buffer(self, buffer: Buffer) -> BufferWrapper:
        buffer_wrapper = BufferWrapper(buffer)
        self._buffer_wrappers.append(buffer_wrapper)
        self._gltf.buffers.append(buffer)
        return buffer_wrapper
        
    def add_triangular_mesh(self, triangular_mesh: TriangularMesh):
        """Add a new mesh given the triangular mesh geometry.

        Args:
            triangular_mesh (TriangularMesh): The triangular mesh.
        """

        triangles = triangular_mesh.triangles_as_array()
        nodes = triangular_mesh.nodes_positions_as_array()

        indices_accessor_index = self._add_accessor_to_bufferview(
            triangles, self._indices_buffer_view, UNSIGNED_INT, SCALAR
        )
        positions_accessor_index = self._add_accessor_to_bufferview(
            nodes, self._positions_buffer_view, FLOAT, VEC3
        )

        primitive = Primitive(
            attributes=Attributes(POSITION=positions_accessor_index),
            indices=indices_accessor_index,
        )
        self._gltf.meshes[self._mesh_index].primitives.append(primitive)
        
        n_frames = len(triangular_mesh.animated_geometry)
        frame_times = []
        weights = []
                
        for frame_index in range(n_frames):
            mesh_geometry = triangular_mesh.animated_geometry[frame_index]
            positions = [node.position.as_list() for node in mesh_geometry]
            nodes = np.array(positions, dtype="float32")

            positions_accessor_index = self._add_accessor_to_bufferview(
                nodes, self._positions_buffer_view, FLOAT, VEC3
            )
            self._positions_buffer_view.byteStride = 12
            
            target_attr = Attributes(POSITION=positions_accessor_index)
            primitive.targets.append(target_attr)
            
            self._mesh.weights.append(0.0)
            
            frame_times.append(float(frame_index))
            weights_for_frame = (n_frames * [0.0])
            weights_for_frame[frame_index] = 1.0
            weights.append(weights_for_frame)
        
        # Add sampler inputs accessor
        sampler_inputs_accessor_index = self._add_accessor_to_bufferview(np.array(frame_times, dtype="float32"), self._sampler_inputs_buffer_view, FLOAT, SCALAR)
        
        # Add sampled outputs accessor
        sampler_outputs_accessor_index = self._add_accessor_to_bufferview(np.array(weights, dtype="float32"), self._sampler_outputs_buffer_view, FLOAT, SCALAR)
        

        sampler = AnimationSampler(input=sampler_inputs_accessor_index, interpolation=ANIM_LINEAR, output=sampler_outputs_accessor_index)
        target = AnimationChannelTarget(node=0, path="weights")
        channel = AnimationChannel(sampler=0, target=target)
        animation = Animation(samplers=[sampler], channels=[channel])
        self._gltf.animations.append(animation)
        
        self._gltf.set_binary_blob(self._binary_blob)

    def _add_accessor_to_bufferview(
        self, data: np.ndarray, buffer_view: BufferView, component_type: int, type: str
    ) -> int:
        data_binary_blob = data.flatten().tobytes()

        # Get offset and length accessor where offset is the offset within the bufferview
        accessor_byte_offset = buffer_view.byteLength
        accessor_byte_length = len(data_binary_blob)

        # Set offset and length buffer view
        buffer_ = self._buffer_wrappers[buffer_view.buffer]
        if buffer_view.byteLength == 0:
            self._set_offset_bufferview_including_padding(buffer_view, buffer_)
        buffer_view.byteLength += accessor_byte_length

        # Set byte length buffer
        buffer_.buffer.byteLength += accessor_byte_length

        # Update binary blob
        self._binary_blob += data_binary_blob
        buffer_.binary_blob += data_binary_blob

        data_max, data_min, data_count = self._get_min_max_count(data, type)
        accessor = Accessor(
            bufferView=self._gltf.bufferViews.index(buffer_view),
            byteOffset=accessor_byte_offset,
            componentType=component_type,
            count=data_count,
            type=type,
            max=data_max,
            min=data_min,
        )
        self._gltf.accessors.append(accessor)

        return self._gltf.accessors.index(accessor)

    def _set_offset_bufferview_including_padding(
        self, buffer_view: BufferView, buffer: BufferWrapper
    ):
        byte_offset = buffer.buffer.byteLength
        n_padding_bytes = (
            byte_offset % 4
        )  # add padding bytes between bufferviews if needed, TODO number of bytes should be according to accessor componenttype,
        if n_padding_bytes != 0:
            byte_offset += n_padding_bytes
            buffer.buffer.byteLength += n_padding_bytes
            self._binary_blob += n_padding_bytes * PADDING_BYTE
            buffer.binary_blob += n_padding_bytes * PADDING_BYTE

        buffer_view.byteOffset = byte_offset

    def _get_min_max_count(self, data: np.ndarray, type: str):
        if type == SCALAR:
            data_max = [int(data.max())]
            data_min = [int(data.min())]
            data_count = data.size
        elif type == VEC3:
            data_max = data.max(axis=0).tolist()
            data_min = data.min(axis=0).tolist()
            data_count = len(data)
        else:
            raise ValueError(f"Type {type} not supported.")

        return data_max, data_min, data_count

    def finish(self) -> GLTF2:
        """Finish the GLTF build and return the results

        Returns:
            GLTF2: The created GLTF2 object.
        """
        return self._gltf
