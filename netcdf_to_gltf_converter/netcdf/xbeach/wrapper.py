import numpy as np
import xarray as xr

from netcdf_to_gltf_converter.netcdf.wrapper import DatasetWrapper, GridWrapper, VariableWrapper, get_coordinate_variables
from netcdf_to_gltf_converter.utils.arrays import uint32_array

class XBeachGrid(GridWrapper):
    
    def __init__(self, dataset: xr.Dataset):
        x_coord_var = get_coordinate_variables(dataset, "projection_x_coordinate")[0]
        y_coord_var = get_coordinate_variables(dataset, "projection_y_coordinate")[0]
        n_vertex_cols = len(x_coord_var.data[0])
        n_vertex_rows = len(x_coord_var.data)
        
        node_index = 0
        
        squares = []
        
        # TODO check if this can be improved
        for _ in range(n_vertex_rows - 1):
            for _ in range(n_vertex_cols - 1):               
                square = [node_index, 
                          node_index + 1,
                          node_index + n_vertex_cols + 1, 
                          node_index + n_vertex_cols, 
                          ]
                squares.append(square)
                
                node_index += 1
            
            node_index += 1

        self._face_node_connectivity = uint32_array(squares)
        
        x_coords = x_coord_var.values.flatten()
        y_coords = y_coord_var.values.flatten()
        self._node_coordinates = np.column_stack([x_coords, y_coords])

    @property
    def face_node_connectivity(self) -> np.ndarray:
        """Get the face node connectivity of the grid.

        Returns:
            np.ndarray: An ndarray of floats with shape (n, 3). Each row represents one face and contains the three node indices that define the face.
        """
        return self._face_node_connectivity

    def set_face_node_connectivity(self, face_node_connectivity: np.ndarray):
        """Set the face node connectivity of the grid.

        Args:
            face_node_connectivity (np.ndarray): An ndarray of floats with shape (n, 3). Each row represents one face and contains the three node indices that define the face.
        """
        self._face_node_connectivity = face_node_connectivity

    @property
    def node_coordinates(self) -> np.ndarray:
        """Get the node coordinates of the grid.

        Returns:
            np.ndarray: An ndarray of floats with shape (n, 2). Each row represents one node and contains the x- and y-coordinate.
        """
        return self._node_coordinates

    @property
    def fill_value(self) -> int:
        """Get the fill value.

        Returns:
            int: Integer with the fill value.
        """
        return -1
    
class XBeachVariable(VariableWrapper):
    """Class that serves as a wrapper object for an xarray.DataArray with UGrid conventions.
    The wrapper allows for easier retrieval of relevant data.
    """

    def __init__(self, data: xr.DataArray) -> None:
        """Initialize a UgridVariable with the specified data.

        Args:
            data (xr.DataArray): The variable data.
        """
        self._data = data
        self._coordinates = self._get_coordinates()

    @property
    def time_index_max(self) -> int:
        """Get the maximum time step index for this data variable.

        Returns:
            int: An integer specifying the maximum time step index.
        """
        return self._data.sizes["globaltime"] - 1

    def get_data_at_time(self, time_index: int) -> np.ndarray:
        """Get the variable values at the specified time index.

        Args:
            time_index (int): The time index.

        Returns:
            np.ndarray: A 1D np.ndarray of floats.
        """
        return self._data.isel(globaltime=time_index).values.flatten()

class XBeachDataset(DatasetWrapper):
    """Class that serves as a wrapper object for an xarray.Dataset with UGrid conventions.
    The wrapper allows for easier retrieval of relevant data.
    """

    def __init__(self, dataset: xr.Dataset) -> None:
        """Initialize a UgridDataset with the specified arguments.

        Args:
            dataset (xr.Dataset): The xarray Dataset.
        """
        dataset = dataset.fillna(0) # TODO check what to do with nan values.
        self._dataset = dataset

    @property
    def grid(self) -> XBeachGrid:
        """Get the XBeachGrid from the data set.

        Returns:
            XBeachGrid: A XBeachGrid created from the data set.
        """        
        return XBeachGrid(self._dataset)
        
    @property
    def min_x(self) -> float:
        """Gets the smallest x-coordinate of the grid.

        Returns:
            float: A floating value with the smallest x-coordinate.
        """
        return self.x_coord_vars[0].values.min()

    @property
    def min_y(self) -> float:
        """Gets the smallest y-coordinate of the grid.

        Returns:
            float: A floating value with the smallest y-coordinate.
        """
        return self.y_coord_vars[0].values.min()

    def get_variable(self, variable_name: str) -> XBeachVariable:
        """Get the variable with the specified name from the data set.

        Args:
            variable_name (str): The variable name.

        Returns:
            UgridVariable: A UgridVariable.

        Raises:
            ValueError: When the dataset does not contain a variable with the name.
        """
        data = self.get_array(variable_name)
        return XBeachVariable(data)