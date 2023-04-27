import base64
from typing import Any, List

import numpy as np
from pygltflib import (
    ANIM_LINEAR,
    ARRAY_BUFFER,
    DATA_URI_HEADER,
    ELEMENT_ARRAY_BUFFER,
    FLOAT,
    GLTF2,
    SCALAR,
    UNSIGNED_INT,
    VEC3,
    VEC4,
    Accessor,
    Animation,
    AnimationChannel,
    AnimationChannelTarget,
    AnimationSampler,
    Attributes,
    Buffer,
    BufferView,
    Mesh,
    Node,
    Primitive,
    Scene,
)

from netcdf_to_gltf_converter.geometries import MeshGeometry, TriangularMesh

PADDING_BYTE = b"\x00"


def add(list: List, item: Any) -> int:
    index = len(list)
    list.append(item)
    return index


class GLTFBuilder:
    def __init__(self) -> None:
        """Initialize a GLTFBuilder.

        Assumption: the GLTF will contain only one scene.
        """

        self._gltf = GLTF2()

        self._mesh_index = add(self._gltf.meshes, Mesh())
        self._node_index = add(self._gltf.nodes, Node(mesh=self._mesh_index))
        self._scene_index = add(self._gltf.scenes, Scene(nodes=[self._node_index]))
        self._gltf.scene = self._scene_index

        # Add a geometry and animation buffer for the mesh
        self._geometry_buffer_index = add(
            self._gltf.buffers, Buffer(byteLength=0, uri=b"")
        )
        self._color_buffer_index = add(
            self._gltf.buffers, Buffer(byteLength=0, uri=b"")
        )
        self._animation_buffer_index = add(
            self._gltf.buffers, Buffer(byteLength=0, uri=b"")
        )

        # Add a buffer view for the indices
        self._indices_buffer_view_index = add(
            self._gltf.bufferViews,
            BufferView(
                buffer=self._geometry_buffer_index,
                byteOffset=0,
                byteLength=0,
                target=ELEMENT_ARRAY_BUFFER,
            ),
        )

        # Add buffer view for the vertex positions and their displacements
        self._positions_buffer_view_index = add(
            self._gltf.bufferViews,
            BufferView(
                buffer=self._geometry_buffer_index,
                byteOffset=0,
                byteLength=0,
                byteStride=12,
                target=ARRAY_BUFFER,
            ),
        )

        self._colors_buffer_view_index = add(
            self._gltf.bufferViews,
            BufferView(
                buffer=self._color_buffer_index,
                byteOffset=0,
                byteLength=0,
            ),
        )

        # Add buffer view for the sampler inputs: the time frames in seconds
        self._time_frames_buffer_view_index = add(
            self._gltf.bufferViews,
            BufferView(buffer=self._animation_buffer_index, byteOffset=0, byteLength=0),
        )

        # Add buffer view for the sampler outputs: the weights per time frame
        self._weights_buffer_view_index = add(
            self._gltf.bufferViews,
            BufferView(buffer=self._animation_buffer_index, byteOffset=0, byteLength=0),
        )

    def add_triangular_mesh(self, triangular_mesh: TriangularMesh):
        """Add a new mesh given the triangular mesh geometry.

        Args:
            triangular_mesh (TriangularMesh): The triangular mesh.
        """

        indices_accessor_index = self._add_accessor_to_bufferview(
            triangular_mesh.triangles,
            self._indices_buffer_view_index,
            UNSIGNED_INT,
            SCALAR,
        )
        positions_accessor_index = self._add_accessor_to_bufferview(
            triangular_mesh.mesh_geometry.vertex_positions,
            self._positions_buffer_view_index,
            FLOAT,
            VEC3,
        )

        colors_accessor_index = self._add_accessor_to_bufferview(
            triangular_mesh.mesh_geometry.vertex_colors,
            self._colors_buffer_view_index,
            FLOAT,
            VEC4,
        )

        primitive = Primitive(
            attributes=Attributes(
                POSITION=positions_accessor_index, COLOR_0=colors_accessor_index
            ),
            indices=indices_accessor_index,
        )
        self._gltf.meshes[self._mesh_index].primitives.append(primitive)

        self.add_mesh_geometry_animation(
            triangular_mesh.mesh_transformations, primitive
        )

    def add_mesh_geometry_animation(
        self, mesh_transformations: List[MeshGeometry], primitive: Primitive
    ):
        n_transformations = len(mesh_transformations)
        time_frames = []
        weights = []

        for frame_index in range(n_transformations):
            mesh_transformation = mesh_transformations[frame_index]

            positions_accessor_index = self._add_accessor_to_bufferview(
                mesh_transformation.vertex_positions,
                self._positions_buffer_view_index,
                FLOAT,
                VEC3,
            )

            target_attr = Attributes(POSITION=positions_accessor_index)
            primitive.targets.append(target_attr)

            self._gltf.meshes[self._mesh_index].weights.append(0.0)

            time_frames.append(float(frame_index))
            weights_for_frame = n_transformations * [0.0]
            weights_for_frame[frame_index] = 1.0
            weights.append(weights_for_frame)

        # Add time frames accessor
        time_frames_inputs_accessor_index = self._add_accessor_to_bufferview(
            np.array(time_frames, dtype="float32"),
            self._time_frames_buffer_view_index,
            FLOAT,
            SCALAR,
        )

        # Add weights accessor
        weights_accessor_index = self._add_accessor_to_bufferview(
            np.array(weights, dtype="float32"),
            self._weights_buffer_view_index,
            FLOAT,
            SCALAR,
        )

        animation = Animation()
        sampler = AnimationSampler(
            input=time_frames_inputs_accessor_index,
            interpolation=ANIM_LINEAR,
            output=weights_accessor_index,
        )
        sample_index = add(animation.samplers, sampler)
        target = AnimationChannelTarget(node=self._node_index, path="weights")
        channel = AnimationChannel(sampler=sample_index, target=target)
        animation.channels.append(channel)

        self._gltf.animations.append(animation)

    def add_data_to_buffer(self, data: bytes, buffer: Buffer):
        buffer.uri += data
        buffer.byteLength += len(data)

    def _add_accessor_to_bufferview(
        self, data: np.ndarray, buffer_view_index: int, component_type: int, type: str
    ) -> int:
        data_binary_blob = data.flatten().tobytes()

        # Get offset and length accessor where offset is the offset within the bufferview
        buffer_view = self._gltf.bufferViews[buffer_view_index]
        accessor_byte_offset = buffer_view.byteLength
        accessor_byte_length = len(data_binary_blob)

        # Set offset and length buffer view
        buffer_ = self._gltf.buffers[buffer_view.buffer]
        if buffer_view.byteLength == 0:
            self._set_offset_bufferview_including_padding(buffer_view, buffer_)
        buffer_view.byteLength += accessor_byte_length

        # Add data to buffer
        self.add_data_to_buffer(data_binary_blob, buffer_)

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

        return add(self._gltf.accessors, accessor)

    def _set_offset_bufferview_including_padding(
        self, buffer_view: BufferView, buffer: Buffer
    ):
        byte_offset = buffer.byteLength
        n_padding_bytes = (
            byte_offset % 4
        )  # add padding bytes between bufferviews if needed, TODO number of bytes should be according to accessor componenttype,
        if n_padding_bytes != 0:
            byte_offset += n_padding_bytes
            self.add_data_to_buffer(n_padding_bytes * PADDING_BYTE, buffer)

        buffer_view.byteOffset = byte_offset

    def _get_min_max_count(self, data: np.ndarray, type: str):
        if type == SCALAR:
            data_max = [int(data.max())]
            data_min = [int(data.min())]
            data_count = data.size
        elif type == VEC3 or type == VEC4:
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
        for buffer in self._gltf.buffers:
            buffer.uri = DATA_URI_HEADER + base64.b64encode(buffer.uri).decode("utf-8")

        return self._gltf
