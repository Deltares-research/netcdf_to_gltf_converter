from typing import List
import numpy as np
import xarray as xr

from netcdf_to_gltf_converter.netcdf.netcdf_data import DatasetBase, get_coordinate_variables
from netcdf_to_gltf_converter.netcdf.xbeach import connectivity

from xugrid.ugrid.conventions import X_STANDARD_NAMES, Y_STANDARD_NAMES

class XBeachGrid():
    """Represents a grid from an XBEACH output file. 
    XBEACH uses regular grids.
    """
    
    def __init__(self, dataset: xr.Dataset):
        """Initialize a new instance of the `XBeachGrid` class.

        Args:
            dataset (xr.Dataset): The dataset retrieved from the netCDF file.
        """
        x_coord_var = get_coordinate_variables(dataset, X_STANDARD_NAMES)[0]
        y_coord_var = get_coordinate_variables(dataset, Y_STANDARD_NAMES)[0]
        n_vertex_cols = len(x_coord_var.data[0])
        n_vertex_rows = len(x_coord_var.data)
        
        self.node_x = x_coord_var.values.flatten()
        self.node_y = y_coord_var.values.flatten()
        self.face_node_connectivity = connectivity.face_node_connectivity_from_regular(n_vertex_rows, n_vertex_cols)

    @property
    def node_coordinates(self) -> np.ndarray:
        """Get the node coordinates of the grid.

        Returns:
            np.ndarray: An ndarray of floats with shape (n, 2). Each row represents one node and contains the x- and y-coordinate.
        """
        return np.column_stack([self.node_x, self.node_y])

class XBeachDataset(DatasetBase):
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
        self._grid = XBeachGrid(dataset)
        
    @property
    def min_x(self) -> float:
        """Gets the smallest x-coordinate of the grid.

        Returns:
            float: A floating value with the smallest x-coordinate.
        """
        return self._x_coord_vars[0].values.min()

    @property
    def min_y(self) -> float:
        """Gets the smallest y-coordinate of the grid.

        Returns:
            float: A floating value with the smallest y-coordinate.
        """
        return self._y_coord_vars[0].values.min()
    
    def transform_coordinate_system(self, source_crs: int, target_crs: int):
        """Transform the coordinates to another coordinate system.
        
        Args:
            source_crs (int): EPSG from the source coordinate system.
            target_crs (int): EPSG from the target coordinate system.

        Raises:
            NotImplementedError: Thrown because coordinate system transformation is not yet suupport for regular grids.
        """
        raise NotImplementedError("Coordinate system transformation is not yet suupport for regular grids.")

    @property
    def face_node_connectivity(self) -> np.ndarray:
        """Get the face node connectivity of the grid.

        Returns:
            np.ndarray: An ndarray of floats with shape (n, 3). Each row represents one face and contains the three node indices that define the face.
        """
        return self._grid.face_node_connectivity

    def set_face_node_connectivity(self, face_node_connectivity: np.ndarray):
        """Set the face node connectivity of the grid.

        Args:
            face_node_connectivity (np.ndarray): An ndarray of floats with shape (n, 3). Each row represents one face and contains the three node indices that define the face.
        """
        self._grid.face_node_connectivity = face_node_connectivity

    @property
    def node_coordinates(self) -> np.ndarray:
        """Get the node coordinates of the grid.

        Returns:
            np.ndarray: An ndarray of floats with shape (n, 2). Each row represents one node and contains the x- and y-coordinate.
        """
        return self._grid.node_coordinates

    @property
    def fill_value(self) -> int:
        """Get the fill value.

        Returns:
            int: Integer with the fill value.
        """
        return -1
    
    def shift_coordinates(self, shift_x: float, shift_y: float) -> None:
        """
        Shift the x- and y-coordinates in the data set with the provided values.
        All x-coordinates will be subtracted with `shift_x`.
        All y_coordinates will be subtracted with `shift_y`.

        Args:
            shift_x (float): The value to shift back the x-coordinates with.
            shift_y (float): The value to shift back the y-coordinates with.
        """

        for x_coord_var in self._x_coord_vars:
            self._shift(x_coord_var, shift_x)

        for y_coord_var in self._y_coord_vars:
            self._shift(y_coord_var, shift_y)
            
        self._update()

    def _update(self):
        self._grid = XBeachGrid(self._dataset)
        
    def _shift(self, variable: xr.DataArray, shift: float):
        shifted_coords_var = variable - shift
        self.set_array(shifted_coords_var)
    
    @property
    def _x_coord_vars(self):  
        return get_coordinate_variables(self._dataset, X_STANDARD_NAMES)  
    
    @property
    def _y_coord_vars(self):  
        return get_coordinate_variables(self._dataset, Y_STANDARD_NAMES)  
     
    def scale_coordinates(self, scale_horizontal: float, scale_vertical: float, variables: List[str]) -> None:
        """
        Scale the x- and y-coordinates and the data values, with the scaling factors that are specified.
        The original data set is updated with the new coordinates.

        Args:
            scale_horizontal (float): The horizontal scale for the x- and y-coordinates of the mesh.
            scale_vertical (float): The vertical scale for the height of the mesh points.
            variables (List[str]): The names of the variables to scale.
        """
        
        if scale_horizontal != 1.0:
            for x_coord_var in self._x_coord_vars:
                self._scale(x_coord_var, scale_horizontal)

            for y_coord_var in self._y_coord_vars:
                self._scale(y_coord_var, scale_horizontal)

        if scale_vertical != 1.0:
            for variable in variables:
                self._scale(self.get_array(variable), scale_vertical)
            
        self._update()
        
    def _scale(self, variable: xr.DataArray, scale: float):
        scaled_coords_var = variable * scale
        self.set_array(scaled_coords_var)