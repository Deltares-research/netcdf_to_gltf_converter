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

    def shift(self) -> xr.Dataset:
        """Shift the x- and y-coordinates, such that the smallest x and y become the origin (0,0).

        Returns:
            xr.Dataset: The dataset with the shifted geometry.
        """
        return self._dataset

    def scale(self) -> xr.Dataset:
        """Scale the x- and y-coordinates, with the scaling factor that is specified in the Config.

        Returns:
            xr.Dataset: The dataset with the scaled geometry.
        """
        return self._dataset
