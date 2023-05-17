import xarray as xr

from netcdf_to_gltf_converter.config import Config
from netcdf_to_gltf_converter.netcdf.wrapper import UgridDataset


class Transformer:
    """A class for transforming the geometry in a dataset."""

    def __init__(self, dataset: UgridDataset, config: Config) -> None:
        """Initialize a Transformer with the specified arguments.

        Args:
            dataset (xr.Dataset): The dataset to transform the coordinates for.
            config (Config): The converter configuration.
        """
        self._dataset = dataset
        self._config = config

    def shift(self):
        """Shift the x- and y-coordinates in the data set, such that the smallest x and y become the origin (0,0).
        The original data set is updated with the shifted coordinates.
        """

        if self._config.shift_coordinates == False:
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

    def _shift(self, coords_var: xr.DataArray, shift: float):
        shifted_coords_var = coords_var - shift
        self._dataset.update(shifted_coords_var)

    def scale(self) -> xr.Dataset:
        """Scale the x- and y-coordinates, with the scaling factor that is specified in the Config.

        Returns:
            xr.Dataset: The dataset with the scaled geometry.
        """
        return self._dataset
