from netcdf_to_gltf_converter.utils.arrays import uint32_array


def face_node_connectivity_from_regular(n_vertex_rows: int, n_vertex_cols: int):
    """Generates the face-node connectivity based on a regular grid 
    with the provided number of rows and columns.

    Args:
        n_vertex_rows (int): The number of vertex rows.
        n_vertex_cols (int): The number of vertex columns.

    Returns:
        np.ndarray: A 2D np.ndarray of floats with shape (nfaces, 4) where each row contains the four node indices of one face. 
    """
    
    node_index = 0
    faces = []
        
    # TODO check if this can be improved
    for _ in range(n_vertex_rows - 1):
        for _ in range(n_vertex_cols - 1):               
            node_indices = [node_index, 
                      node_index + 1,
                      node_index + n_vertex_cols + 1, 
                      node_index + n_vertex_cols, 
                      ]
            faces.append(node_indices)  
            node_index += 1
        node_index += 1

    return uint32_array(faces)