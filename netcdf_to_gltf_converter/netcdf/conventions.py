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