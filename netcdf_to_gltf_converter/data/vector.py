from dataclasses import dataclass


@dataclass
class Vec3:
    """Data class representing a vector with 3 values."""

    x: float = 0.0
    """float: x. Defaults to 0.0."""

    y: float = 0.0
    """float: y. Defaults to 0.0."""

    z: float = 0.0
    """float: z. Defaults to 0.0."""
