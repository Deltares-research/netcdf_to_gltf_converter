from typing import List

import numpy as np
import pyproj
import xarray as xr
import xugrid as xu

from netcdf_to_gltf_converter.netcdf.netcdf_data import DatasetBase


class UgridDataset(DatasetBase):
    """Class that serves as a wrapper object for an xarray.Dataset with UGrid conventions.
    The wrapper allows for easier retrieval of relevant data.
    """

    def __init__(self, dataset: xr.Dataset) -> None:
        """Initialize a UgridDataset with the specified arguments.

        Args:
            dataset (xr.Dataset): The xarray Dataset.
        """
        super().__init__(dataset)
        self._ugrid_data_set = xu.UgridDataset(dataset)  
        self._grid = self._get_ugrid2d()

    @property
    def min_x(self) -> float:
        """Gets the smallest x-coordinate of the grid.

        Returns:
            float: A floating value with the smallest x-coordinate.
        """
        min_x, _, _,_ = self._grid.bounds
        return min_x

    @property
    def min_y(self) -> float:
        """Gets the smallest y-coordinate of the grid.

        Returns:
            float: A floating value with the smallest y-coordinate.
        """
        _, min_y, _,_ = self._grid.bounds
        return min_y

    def _get_ugrid2d(self) -> xu.Ugrid2d:
        for grid in self._ugrid_data_set.grids:
            if isinstance(grid, xu.Ugrid2d):
                return grid
        
        raise ValueError("No 2D grid")

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
        return self._grid.fill_value
    
    def transform_coordinate_system(self, source_epsg: int, target_epsg: int):
        """Transform the coordinates to another coordinate system.
        Args:
            source_epsg (int): EPSG from the source coordinate system.
            target_epsg (int): EPSG from the target coordinate system.

        """
        source_epsg = pyproj.CRS.from_epsg(source_epsg)
        target_epsg = pyproj.CRS.from_epsg(target_epsg)
                                          
        transformer = pyproj.Transformer.from_crs(
            crs_from=source_epsg, crs_to=target_epsg, always_xy=True
        )
        
        node_x2, node_y2 = transformer.transform(self._grid.node_x, self._grid.node_y)
        
        self._grid.node_x = node_x2
        self._grid.node_y = node_y2
        
        self._update()
        
    def shift_coordinates(self, shift_x: float, shift_y: float) -> None:
        """
        Shift the x- and y-coordinates in the data set with the provided values.
        All x-coordinates will be subtracted with `shift_x`.
        All y_coordinates will be subtracted with `shift_y`.

        Args:
            shift_x (float): The value to shift back the x-coordinates with.
            shift_y (float): The value to shift back the y-coordinates with.
        """
               
        self._grid.node_x = self._grid.node_x - shift_x
        self._grid.node_y = self._grid.node_y - shift_y
        self._update()
        
    def scale_coordinates(self, scale_horizontal: float, scale_vertical: float, variables: List[str]) -> None:
        """
        Scale the x- and y-coordinates and the data values, with the scaling factors that are specified.
        The original data set is updated with the new coordinates.

        Args:
            scale_horizontal (float): The horizontal scale for the x- and y-coordinates of the mesh.
            scale_vertical (float): The vertical scale for the height of the mesh points.
            variables (List[str]): The names of the variables to scale.
        """     
        self._grid.node_x = self._grid.node_x * scale_horizontal
        self._grid.node_y = self._grid.node_y * scale_horizontal          
        self._update()
        
        for variable_name in variables:
            variable = self.get_array(variable_name)
            scaled_coords_var = variable * scale_vertical
            self.set_array(scaled_coords_var)
            
    def _update(self):
        self._grid._clear_geometry_properties()
        self._ugrid_data_set: xu.UgridDataset = self._ugrid_data_set.ugrid.assign_node_coords().ugrid.assign_face_coords().ugrid.assign_edge_coords()
        self._dataset = self._ugrid_data_set.obj