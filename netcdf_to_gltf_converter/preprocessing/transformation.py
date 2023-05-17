import xarray as xr

from netcdf_to_gltf_converter.config import Config
from netcdf_to_gltf_converter.netcdf.wrapper import UgridDataset

xr.set_options(keep_attrs=True)
"""Attributes need to be preserved when creating a new DataArray with a transformation."""


class Transformer:
    """A class for transforming the geometry in a dataset."""

    def __init__(self, dataset: UgridDataset, config: Config) -> None:
        """Initialize a Transformer with the specified arguments.

        Args:
            dataset (xr.UgridDataset): The Ugrid dataset to transform the coordinates for.
            config (Config): The converter configuration.
        """
        self._dataset = dataset
        self._config = config

    def shift(self):
        """
        If shifting is required, shift the x- and y-coordinates in the data set, such that the smallest x and y become the origin (0,0).
        The original data set is updated with the new coordinates.
        """

        if not self._config.shift_coordinates:
            return

        node_x_var, node_y_var = self._dataset.node_coord_vars
        edge_x_var, edge_y_var = self._dataset.edge_coord_vars
        face_x_var, face_y_var = self._dataset.face_coord_vars

        shift_x = node_x_var.values.min()
        shift_y = node_y_var.values.min()

        self._shift(node_x_var, shift_x)
        self._shift(node_y_var, shift_y)
        self._shift(edge_x_var, shift_x)
        self._shift(edge_y_var, shift_y)
        self._shift(face_x_var, shift_x)
        self._shift(face_y_var, shift_y)

    def _shift(self, variable: xr.DataArray, shift: float):
        shifted_coords_var = variable - shift
        self._dataset.set_variable(shifted_coords_var)

    def scale(self):
        """
        If scaling is required, scale the x- and y-coordinates and the data values, with the scaling factor that is specified in the Config.
        The original data set is updated with the new coordinates.
        """

        if self._config.scale == 1.0:
            return

        node_x_var, node_y_var = self._dataset.node_coord_vars
        edge_x_var, edge_y_var = self._dataset.edge_coord_vars
        face_x_var, face_y_var = self._dataset.face_coord_vars

        self._scale(node_x_var)
        self._scale(node_y_var)
        self._scale(edge_x_var)
        self._scale(edge_y_var)
        self._scale(face_x_var)
        self._scale(face_y_var)

        self._scale_data()

    def _scale(self, variable: xr.DataArray):
        scaled_coords_var = variable * self._config.scale
        self._dataset.set_variable(scaled_coords_var)

    def _scale_data(self):
        for variable in self._config.variables:
            variable = self._dataset.get_variable(variable.name)
            self._scale(variable)
