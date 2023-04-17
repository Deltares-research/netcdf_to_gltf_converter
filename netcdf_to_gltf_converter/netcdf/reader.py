from enum import Enum
from pathlib import Path

import cf_xarray
import xarray as xr


class StandardName(str, Enum):
    """Enum containg the valid variable standard names according to the
    NetCDF Climate and Forecast (CF) Metadata Conventions version 1.8.
    See also: http://cfconventions.org/Data/cf-standard-names/current/build/cf-standard-name-table.html
    """

    water_depth = "sea_floor_depth_below_sea_surface"
    """The vertical distance between the sea surface and the seabed as measured at a given point in space including the variance caused by tides and possibly waves."""


class MeshType(str, Enum):
    """Enum containg the valid mesh types as stored in the "mesh" attribute of a data variable."""

    mesh1d = "mesh1d"
    """1D mesh"""
    mesh2d = "Mesh2d"
    """2D mesh"""


class Variable:
    def __init__(self, data: xr.DataArray):
        self._data = data


class Dataset:
    def __init__(self, dataset: xr.Dataset) -> None:
        self._ds = dataset

    def get_water_depth_2d(self) -> Variable:
        ds_mesh2d: xr.Dataset = self._ds.filter_by_attrs(mesh=MeshType.mesh2d)
        ds_water_depth: xr.DataArray = ds_mesh2d.cf[StandardName.water_depth]

        return Variable(data=ds_water_depth)


class Reader:
    def read(self, file: Path) -> Dataset:
        ds: xr.Dataset = xr.open_dataset(file)
        return Dataset(dataset=ds)
