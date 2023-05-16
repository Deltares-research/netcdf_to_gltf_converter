from enum import Enum


class AttrKey(str, Enum):
    """Enum containing variable attribute keys."""

    cf_role = "cf_role"
    """CF role"""
    topology_dimension = "topology_dimension"
    """Topology dimension"""
    mesh = "mesh"
    """Mesh"""
    standard_name = "standard_name"
    """Standard name"""
    location = "location"
    """Mesh location of the data"""


class AttrValue(str, Enum):
    """Enum containing variable attribute values."""

    mesh_topology = "mesh_topology"
    """Mesh topology"""

class StandardName(str, Enum):
    """Enum containg the valid variable standard names according to the
    NetCDF Climate and Forecast (CF) Metadata Conventions version 1.8.
    See also: http://cfconventions.org/Data/cf-standard-names/current/build/cf-standard-name-table.html
    """

    water_depth = "sea_floor_depth_below_sea_surface"
    """The vertical distance between the sea surface and the seabed as measured at a given point in space including the variance caused by tides and possibly waves."""
    water_level = "sea_surface_height"
    """"Sea surface height" is a time-varying quantity."""