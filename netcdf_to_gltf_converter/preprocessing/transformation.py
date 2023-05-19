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


def scale(dataset: DatasetWrapper, variables: List[str], scale: float):
    """
    If scaling is required, scale the x- and y-coordinates and the data values, with the scaling factor that is specified in the Config.
    The original data set is updated with the new coordinates.

    Args:
        dataset (DatasetWrapper): The dataset to transform the coordinates for.
        variables (List[str]): The names of the variables to scale.
    """

    for x_coord_var in dataset.x_coord_vars:
        _scale(x_coord_var, dataset, scale)

    for y_coord_var in dataset.y_coord_vars:
        _scale(y_coord_var, dataset, scale)

    _scale_data(dataset, variables, scale)


def _scale(variable: xr.DataArray, dataset: DatasetWrapper, scale: float):
    scaled_coords_var = variable * scale
    dataset.set_array(scaled_coords_var)


def _scale_data(dataset: DatasetWrapper, variables: List[str], scale: float):
    for variable in variables:
        _scale(dataset.get_array(variable), dataset, scale)
