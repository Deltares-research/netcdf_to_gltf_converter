from enum import Enum


class AttrKey(str, Enum):
    """Enum containing variable attribute keys."""

    cf_role = "cf_role"
    """CF role"""
    topology_dimension = "topology_dimension"
    """Topology dimension"""


class CfRoleAttrValue(str, Enum):
    """Enum containing variable attribute values for the 'cf_role' attribute."""

    mesh_topology = "mesh_topology"
    """Mesh topology"""
