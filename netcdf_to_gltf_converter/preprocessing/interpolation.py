from enum import Enum

import numpy as np
import xugrid as xu
from scipy import interpolate


class Method(str, Enum):
    linear = "linear"
    nearest = "nearest"


class Location(str, Enum):
    """The interpolation location for the grid."""

    nodes = "nodes"
    """Interpolate on the node coordinates of the grid."""
    faces = "faces"
    """Interpolate on the face coordinates of the grid."""
    edges = "edges"
    """Interpolate on the edge coordinates of the grid."""


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

    def interpolate_nearest(
        self,
        data_coords: np.ndarray,
        data_values: np.ndarray,
        grid: xu.Ugrid2d,
        location: Location,
    ) -> np.ndarray:
        """Interpolate the data values onto the points to interpolate.
        Interpolation is performend by taking the data point closest to the point of interpolation.

        Args:
            data_coords (np.ndarray): The data point coordinates, a 2D ndarray of floats with shape (n, 2) where each row contains a x and y coordinate.
            data_values (np.ndarray): The data point values, a 1D ndarray of floats with shape (n,).
            grid (xu.Ugrid2d): The grid onto which to interpolate the data.
            location (Location): The grid element type onto which to interpolate the data.

        Returns:
            np.ndarray: The interpolated data values, an ndarray of floats with shape (m, 3). Each row contains the x and y coordinate with the interpolated value.

        Raises:
            ValueError: When the provided location is not supported.
        """

        return self._interpolate(
            data_coords, data_values, grid, location, Method.nearest
        )

    def interpolate_linear(
        self,
        data_coords: np.ndarray,
        data_values: np.ndarray,
        grid: xu.Ugrid2d,
        location: Location,
    ) -> np.ndarray:
        """Interpolate the data values onto the points to interpolate.
        Interpolation is performend by triangulating the input data, and on each triangle performing linear interpolation.

        Args:
            data_coords (np.ndarray):  The data point coordinates, a 2D ndarray of floats with shape (n, 2) where each row contains a x and y coordinate.
            data_values (np.ndarray): The data point values, a 1D ndarray of floats with shape (n,).grid (xu.Ugrid2d): The grid onto which to interpolate the data.
            grid (xu.Ugrid2d): The grid onto which to interpolate the data.
            location (Location): The grid element type onto which to interpolate the data.

        Returns:
            np.ndarray: The interpolated data values, an ndarray of floats with shape (m, 3). Each row contains the x and y coordinate with the interpolated value.

        Raises:
            ValueError: When the provided location is not supported.
        """

        return self._interpolate(
            data_coords, data_values, grid, location, Method.linear
        )

    def _interpolate(
        self,
        data_coords: np.ndarray,
        data_values: np.ndarray,
        grid: xu.Ugrid2d,
        location: Location,
        method: Method,
    ) -> np.ndarray:
        points_to_interpolate = Interpolator.get_coordinates(grid, location)

        interpolated_points = interpolate.griddata(
            data_coords,
            data_values,
            points_to_interpolate,
            method=method,
        )

        return np.concatenate(
            (points_to_interpolate, interpolated_points.reshape(-1, 1)),
            axis=1,
            dtype=np.float32,
        )
