from typing import List

import numpy as np
import xarray as xr

from netcdf_to_gltf_converter.netcdf.wrapper import DatasetWrapper

xr.set_options(keep_attrs=True)
"""Attributes need to be preserved when creating a new DataArray with a transformation."""


def shift(dataset: DatasetWrapper):
    """
    Shift the x- and y-coordinates in the data set, such that the smallest x and y become the origin (0,0).
    The original data set is updated with the new coordinates.

    Args:
        dataset (DatasetWrapper): The dataset to transform the coordinates for.
        config (Config): The converter configuration.
    """

    shift_x = dataset.min_x
    shift_y = dataset.min_y

    for x_coord_var in dataset.x_coord_vars:
        _shift(x_coord_var, shift_x, dataset)

    for y_coord_var in dataset.y_coord_vars:
        _shift(y_coord_var, shift_y, dataset)


def _shift(variable: xr.DataArray, shift: float, dataset: DatasetWrapper):
    shifted_coords_var = variable - shift
    dataset.set_array(shifted_coords_var)


def scale(dataset: DatasetWrapper, variables: List[str], scale_horizontal: float, scale_vertical: float):
    """
    If scaling is required, scale the x- and y-coordinates and the data values, with the scaling factors that are specified.
    The original data set is updated with the new coordinates.

    Args:
        dataset (DatasetWrapper): The dataset to transform the coordinates for.
        variables (List[str]): The names of the variables to scale.
        scale_horizontal (float): The horizontal scale for the x- and y-coordinates of the mesh.
        scale_vertical (float): The vertical scale for the height of the mesh points.
    """

    if scale_horizontal != 1.0:
        for x_coord_var in dataset.x_coord_vars:
            _scale(x_coord_var, dataset, scale_horizontal)

        for y_coord_var in dataset.y_coord_vars:
            _scale(y_coord_var, dataset, scale_horizontal)

    if scale_vertical != 1.0:
        _scale_data(dataset, variables, scale_vertical)


def _scale(variable: xr.DataArray, dataset: DatasetWrapper, scale: float):
    scaled_coords_var = variable * scale
    dataset.set_array(scaled_coords_var)


def _scale_data(dataset: DatasetWrapper, variables: List[str], scale: float):
    for variable in variables:
        _scale(dataset.get_array(variable), dataset, scale)
