from abc import ABC, abstractmethod
from enum import Enum

import numpy as np
from scipy import interpolate

from netcdf_to_gltf_converter.netcdf.netcdf_data import GridBase


class Method(str, Enum):
    linear = "linear"
    nearest = "nearest"


class InterpolatorBase(ABC):
    """Class to interpolate data values onto a set of coordinates."""

    @abstractmethod
    def interpolate(
        self,
        data_coords: np.ndarray,
        data_values: np.ndarray,
        grid: GridBase,
    ) -> np.ndarray:
        """Interpolate the data values onto the points to interpolate.
        Interpolation is performend by taking the data point closest to the point of interpolation.

        Args:
            data_coords (np.ndarray): The data point coordinates, a 2D ndarray of floats with shape (n, 2) where each row contains a x and y coordinate.
            data_values (np.ndarray): The data point values, a 1D ndarray of floats with shape (n,).
            grid (GridBase): The grid onto which to interpolate the data.

        Returns:
            np.ndarray: The interpolated data values, an ndarray of floats with shape (m, 3). Each row contains the x and y coordinate with the interpolated value.
        """

        pass

    def _interpolate(
        self,
        data_coords: np.ndarray,
        data_values: np.ndarray,
        grid: GridBase,
        method: Method,
    ) -> np.ndarray:
        points_to_interpolate = grid.node_coordinates

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


class NearestPointInterpolator(InterpolatorBase):
    """Class to interpolate data values onto a set of coordinates using nearest point interpolation."""

    def interpolate(
        self,
        data_coords: np.ndarray,
        data_values: np.ndarray,
        grid: GridBase,
    ) -> np.ndarray:
        """Interpolate the data values onto the points to interpolate.
        Interpolation is performend by taking the data point closest to the point of interpolation.

        Args:
            data_coords (np.ndarray): The data point coordinates, a 2D ndarray of floats with shape (n, 2) where each row contains a x and y coordinate.
            data_values (np.ndarray): The data point values, a 1D ndarray of floats with shape (n,).
            grid (GridBase): The grid onto which to interpolate the data.

        Returns:
            np.ndarray: The interpolated data values, an ndarray of floats with shape (m, 3). Each row contains the x and y coordinate with the interpolated value.
        """

        return self._interpolate(data_coords, data_values, grid, Method.nearest)


class LinearInterpolator(InterpolatorBase):
    """Class to interpolate data values onto a set of coordinates using linear interpolation."""

    def interpolate(
        self,
        data_coords: np.ndarray,
        data_values: np.ndarray,
        grid: GridBase,
    ) -> np.ndarray:
        """Interpolate the data values onto the points to interpolate.
        Interpolation is performend by triangulating the input data, and on each triangle performing linear interpolation.

        Args:
            data_coords (np.ndarray):  The data point coordinates, a 2D ndarray of floats with shape (n, 2) where each row contains a x and y coordinate.
            data_values (np.ndarray): The data point values, a 1D ndarray of floats with shape (n,).
            grid (GridBase): The grid onto which to interpolate the data.

        Returns:
            np.ndarray: The interpolated data values, an ndarray of floats with shape (m, 3). Each row contains the x and y coordinate with the interpolated value.
        """

        return self._interpolate(data_coords, data_values, grid, Method.linear)
