import base64
from typing import Any, List

import numpy as np
from pygltflib import (ANIM_LINEAR, ARRAY_BUFFER, DATA_URI_HEADER,
                       ELEMENT_ARRAY_BUFFER, FLOAT, GLTF2, SCALAR,
                       UNSIGNED_INT, VEC3, VEC4, Accessor, Animation,
                       AnimationChannel, AnimationChannelTarget,
                       AnimationSampler, Attributes, Buffer, BufferView,
                       Material, Mesh, Node, PbrMetallicRoughness, Primitive,
                       Scene)

from netcdf_to_gltf_converter.data.mesh import TriangularMesh
from netcdf_to_gltf_converter.utils.arrays import float32_array

PADDING_BYTE = b"\x00"
ROTATION_MATRIX = [-0.9998477, 0, 0.0174524, 0,
                    0.0174524, 0, 0.9998477, 0,
                    0, 1, 0, 0,
                    0, 0, 0, 1]
"""Rotation matrix to flip the y and z axes and rotate the model 179 degrees around the up-axis."""

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
        self._scene_index = add(self._gltf.scenes, Scene())
        self._gltf.scene = self._scene_index

    def add_triangular_mesh(self, triangular_mesh: TriangularMesh):
        """Add a new mesh given the triangular mesh geometry.

        Args:
            triangular_mesh (TriangularMesh): The triangular mesh.
        """

        material_model = PbrMetallicRoughness(
            metallicFactor=triangular_mesh.metallic_factor,
            roughnessFactor=triangular_mesh.roughness_factor,
        )
        material = Material(pbrMetallicRoughness=material_model)
        material_index = add(self._gltf.materials, material)
        mesh_index = add(self._gltf.meshes, Mesh())
        node_index = add(self._gltf.nodes, Node(mesh=mesh_index, matrix=ROTATION_MATRIX))
        scene = self._gltf.scenes[self._scene_index]
        scene.nodes.append(node_index)

        # Add a buffer for the mesh geometry, colors and animation
        geometry_buffer_index = add(self._gltf.buffers, Buffer(byteLength=0, uri=b""))
        color_buffer_index = add(self._gltf.buffers, Buffer(byteLength=0, uri=b""))

        # Add a buffer view for the indices
        indices_buffer_view_index = add(
            self._gltf.bufferViews,
            BufferView(
                buffer=geometry_buffer_index,
                byteOffset=0,
                byteLength=0,
                target=ELEMENT_ARRAY_BUFFER,
            ),
        )

        # Add buffer view for the vertex positions and their displacements
        positions_buffer_view_index = add(
            self._gltf.bufferViews,
            BufferView(
                buffer=geometry_buffer_index,
                byteOffset=0,
                byteLength=0,
                byteStride=12,
                target=ARRAY_BUFFER,
            ),
        )

        # Add buffer view for the vertex colors
        colors_buffer_view_index = add(
            self._gltf.bufferViews,
            BufferView(
                buffer=color_buffer_index,
                byteOffset=0,
                byteLength=0,
            ),
        )

        indices_accessor_index = self._add_accessor_to_bufferview(
            triangular_mesh.triangles,
            indices_buffer_view_index,
            UNSIGNED_INT,
            SCALAR,
        )
        positions_accessor_index = self._add_accessor_to_bufferview(
            triangular_mesh.base.vertex_positions,
            positions_buffer_view_index,
            FLOAT,
            VEC3,
        )
        colors_accessor_index = self._add_accessor_to_bufferview(
            triangular_mesh.base.vertex_colors,
            colors_buffer_view_index,
            FLOAT,
            VEC4,
        )

        primitive = Primitive(
            attributes=Attributes(
                POSITION=positions_accessor_index, COLOR_0=colors_accessor_index
            ),
            indices=indices_accessor_index,
            material=material_index,
        )
        self._gltf.meshes[mesh_index].primitives.append(primitive)

        n_transformations = len(triangular_mesh.transformations)
        if n_transformations == 0:
            return

        animation_buffer_index = add(self._gltf.buffers, Buffer(byteLength=0, uri=b""))

        # Add buffer view for the sampler inputs: the time frames in seconds
        time_frames_buffer_view_index = add(
            self._gltf.bufferViews,
            BufferView(buffer=animation_buffer_index, byteOffset=0, byteLength=0),
        )

        # Add buffer view for the sampler outputs: the weights per time frame
        weights_buffer_view_index = add(
            self._gltf.bufferViews,
            BufferView(buffer=animation_buffer_index, byteOffset=0, byteLength=0),
        )

        time_frames = []
        weights = []

        for frame_index, transformation in enumerate(triangular_mesh.transformations):
            positions_accessor_index = self._add_accessor_to_bufferview(
                transformation.vertex_positions,
                positions_buffer_view_index,
                FLOAT,
                VEC3,
            )

            target_attr = Attributes(POSITION=positions_accessor_index)
            primitive.targets.append(target_attr)

            self._gltf.meshes[mesh_index].weights.append(0.0)

            time_frames.append(float(frame_index))

            weights_for_frame = n_transformations * [0.0]
            weights_for_frame[frame_index] = 1.0
            weights.append(weights_for_frame)

        # Add time frames accessor
        time_frames_accessor_index = self._add_accessor_to_bufferview(
            float32_array(time_frames),
            time_frames_buffer_view_index,
            FLOAT,
            SCALAR,
        )

        # Add weights accessor
        weights_accessor_index = self._add_accessor_to_bufferview(
            float32_array(weights),
            weights_buffer_view_index,
            FLOAT,
            SCALAR,
        )

        animation = Animation()
        sampler = AnimationSampler(
            input=time_frames_accessor_index,
            interpolation=ANIM_LINEAR,
            output=weights_accessor_index,
        )
        sample_index = add(animation.samplers, sampler)
        target = AnimationChannelTarget(node=node_index, path="weights")
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
