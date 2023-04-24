from enum import Enum

import numpy as np
from scipy import interpolate


class Interpolator:
    """Class to interpolate data values onto a set of coordinates."""

    class Method(str, Enum):
        linear = "linear"
        nearest = "nearest"

    @staticmethod
    def interpolate_nearest(
        data_points: np.ndarray,
        data_values: np.ndarray,
        points_to_interpolate: np.ndarray,
    ) -> np.ndarray:
        """Interpolate the data values onto the points to interpolate.
        Interpolation is performend by taking the data point closest to the point of interpolation.

        Args:

            data_points (np.ndarray): The data point coordinates, a 2D ndarray of floats with shape (n, 2).
            data_values (np.ndarray): The data values, an ndarray of floats with shape (n,).
            grid_points (np.ndarray): The points at which to interpolate data, a 2D ndarray of floats with shape (m, 2).

        Returns:
            np.ndarray: The interpolated data values, an ndarray of floats with shape (m,).
        """
        return interpolate.griddata(
            data_points,
            data_values,
            points_to_interpolate,
            method=Interpolator.Method.nearest,
        )

    def interpolate_linear(
        data_points: np.ndarray,
        data_values: np.ndarray,
        points_to_interpolate: np.ndarray,
    ) -> np.ndarray:
        """Interpolate the data values onto the points to interpolate.
        Interpolation is performend by triangulating the input data, and on each triangle performing linear interpolation.

        Args:
            data_points (np.ndarray): The data point coordinates, a 2D ndarray of floats with shape (n, 2).
            data_values (np.ndarray): The data values, an ndarray of floats with shape (n,).
            grid_points (np.ndarray): The points at which to interpolate data, a 2D ndarray of floats with shape (m, 2).

        Returns:
            np.ndarray: The interpolated data values, an ndarray of floats with shape (m,).
        """
        return interpolate.griddata(
            data_points,
            data_values,
            points_to_interpolate,
            method=Interpolator.Method.linear,
        )
