from enum import Enum
import xugrid as xu
import numpy as np
from scipy import interpolate

class Method(str, Enum):
    linear = "linear"
    nearest = "nearest"

class Location(str, Enum):
    nodes = "nodes"
    faces = "faces"
    edges = "edges"

class Interpolator:
    """Class to interpolate data values onto a set of coordinates."""

    @staticmethod
    def get_coordinates(grid: xu.Ugrid2d, location: Location):
        if location == Location.nodes:
            return grid.node_coordinates
        if location == Location.faces:
            return grid.face_coordinates
        if location == Location.edges:
            return grid.edge_coordinates
        
        raise ValueError(f"Invalid location {location}")
        
    @staticmethod
    def interpolate_nearest(
        data_points: np.ndarray,
        data_values: np.ndarray,
        grid: xu.Ugrid2d,
        location: Location
    ) -> np.ndarray:
        """Interpolate the data values onto the points to interpolate.
        Interpolation is performend by taking the data point closest to the point of interpolation.

        Args:
            data_points (np.ndarray): The data point coordinates, a 2D ndarray of floats with shape (n, 2).
            data_values (np.ndarray): The data values, an ndarray of floats with shape (n,).
            grid (xu.Ugrid2d): The grid onto which to interpolate the data.
            location (Location): The grid element type onto which to interpolate the data.

        Returns:
            np.ndarray: The interpolated data values, an ndarray of floats with shape (m, 3).
            
        Raises: 
            ValueError: When the provided location is not supported.
        """
        
        return Interpolator._interpolate(data_points, data_values, grid, location, Method.nearest)

    @staticmethod
    def interpolate_linear(
        data_points: np.ndarray,
        data_values: np.ndarray,
        grid: xu.Ugrid2d,
        location: Location
    ) -> np.ndarray:
        """Interpolate the data values onto the points to interpolate.
        Interpolation is performend by triangulating the input data, and on each triangle performing linear interpolation.

        Args:
            data_points (np.ndarray): The data point coordinates, a 2D ndarray of floats with shape (n, 2).
            data_values (np.ndarray): The data values, an ndarray of floats with shape (n,).
            grid (xu.Ugrid2d): The grid onto which to interpolate the data.
            location (Location): The grid element type onto which to interpolate the data.
            
        Returns:
            np.ndarray: The interpolated data values, an ndarray of floats with shape (m, 3).
            
        Raises: 
            ValueError: When the provided location is not supported.
        """
        
        return Interpolator._interpolate(data_points, data_values, grid, location, Method.linear)
        
    def _interpolate(
        data_points: np.ndarray,
        data_values: np.ndarray,
        grid: xu.Ugrid2d,
        location: Location,
        method: Method
        
    ) -> np.ndarray:
        
        points_to_interpolate = Interpolator.get_coordinates(grid, location)
        
        interpolated_points = interpolate.griddata(
            data_points,
            data_values,
            points_to_interpolate,
            method=method,
        )
        
        return np.concatenate((points_to_interpolate, interpolated_points.reshape(-1, 1)), axis=1)
