import logging
from abc import ABC
from pathlib import Path
from typing import List, Optional, Type, TypeVar

from packaging.version import Version
from pydantic import BaseModel as PydanticBaseModel
from pydantic import Extra, Field, validator


class BaseModel(PydanticBaseModel):
    """BaseModel defines the base for Pydantic model classes."""

    class Config:
        arbitrary_types_allowed = True
        validate_assignment = True
        ase_enum_values = True
        extra = Extra.forbid
        allow_population_by_field_name = True


class AbstractFileVersionFile(BaseModel, ABC):
    """Baseclass for files with file versions."""

    _expected_file_version: Version

    file_version: Optional[Version] = None
    """Optional[Version]: The file version of this AbstractFileVersionFile."""

    class Config:
        json_encoders = {
            Version: lambda v: v.public,
        }

    @validator("file_version", pre=True)
    def convert_string_to_version(cls, v):
        if isinstance(v, str):
            v = Version(v)
        return v

    @validator("file_version")
    def validate_file_version(cls, v):
        """Validate the file version. The version should be greated than or equal to the expected file version."""

        max_major_version = Version(f"{cls._expected_file_version.major + 1}")

        if v is None:
            msg = (
                "%s: No file version provided, expected version, %s. The behaviour "
                "might be undefined or incorrect."
            )
            logging.warning(msg, cls._filename, cls._expected_file_version)
        elif not (cls._expected_file_version <= v < max_major_version):
            msg = (
                "%s: The provided file version, %s, is not compatible with the "
                "expected version, %s. The behaviour might be undefined or incorrect."
            )
            logging.warning(
                msg, cls._filename, v.public, cls._expected_file_version.public
            )

        return v


TJsonConfigFile = TypeVar("TJsonConfigFile", bound="AbstractJsonConfigFile")


class AbstractJsonConfigFile(BaseModel, ABC):
    """Baseclass for Json config files. Provides the from_file method to load the
    data and provide the necessary logging behavior.
    """

    @classmethod
    def from_file(cls: Type[TJsonConfigFile], path: Path) -> TJsonConfigFile:
        """Create a new AbstractJsonConfigFile from the specified path.

        Args:
            path (Path): The path to the configuration file.

        Returns:
            cls: An instance of the cls.
        """

        if not path.is_file():
            raise ValueError(f"Config file does not exist: {path}")

        return cls.parse_file(path)


class Threshold(BaseModel):
    """Configuration properties of a variable threshold mesh."""

    color: List[float] = Field(alias="color")
    """List[float]: The vertex color in the threshold mesh defined by the normalized red, green, blue and alpha (RGBA) values."""
    height: float = Field(alias="height")
    """float: The height (vertex z-values) of the threshold mesh."""

    @validator("color")
    def validate_color(cls, color):
        """Validate the color. The color should be a list that contains 4 floating values between 0.0 and 1.0 (inclusive)."""

        if len(color) != 4:
            msg = "A color should be defined as a list of 4 floating values: the normalized red, green, blue and alpha (RGBA) values."
            raise ValueError(msg)

        for channel in color:
            if not 0 <= channel <= 1:
                msg = f"The color channel {channel} is outside of range 0.0-1.0. A color should be defined by the normalized red, green, blue and alpha (RGBA) values."
                raise ValueError(msg)

        return color


class Variable(BaseModel):
    """Configuration properties of a variable."""

    standard_name: str = Field("standard_name")
    """str: The standard name of the NetCDF variable"""
    threshold: Optional[Threshold] = Field(None, alias="threshold")
    """Optional[Threshold]: The threshold mesh configuration properties."""


class Config(AbstractJsonConfigFile, AbstractFileVersionFile):
    """The configuration settings described in the configuration JSON file."""

    _expected_file_version = Version("0.1.0")

    shift_coordinates: bool = Field(alias="shift_coordinates")
    """bool: Whether or not to shift the x- and y-coordinates, such that the smallest x and y become the origin (0,0)."""
    scale: float = Field(alias="scale")
    """float: The scale of the mesh coordinates compared to the coordinates from file."""
    variables: List[Variable] = Field(alias="variables")
    """List[Variable]: List of configuration of the variables that should be converted to glTF."""