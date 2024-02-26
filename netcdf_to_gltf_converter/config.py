import logging
from abc import ABC
from pathlib import Path
from typing import Any, Dict, List, Optional, Type, TypeVar, Union

from packaging.version import Version
from pydantic import BaseModel as PydanticBaseModel
from pydantic import Extra, root_validator, validator
from strenum import StrEnum

from netcdf_to_gltf_converter.utils.validation import in_range

Color = List[float]

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

class ModelType(StrEnum):
    """The model type of the input data."""
    
    DHYDRO = "D-HYDRO"
    """Output from a D-HYDRO model (UGRID)."""
    
    XBEACH = "XBEACH"
    """Output from an XBEACH model (regular grid)."""

class ShiftType(StrEnum):
    """The method to shift the coordinates."""
    
    MIN = "min"
    """The smalles x- and -y coordinate become the origin (0,0)."""
    
class CrsTransformation(BaseModel):
    """The configuration settings for transforming the coordinates."""

    source_epsg: int
    """int: EPSG code of the course coordinate system."""

    target_epsg: int
    """int: EPSG code of the target coordinate system."""

class CrsShifting(BaseModel):
    """The configuration settings for shifting the coordinates."""

    shift_x: float
    """float: Value to shift the x-coordinates with. All x-coordinates will be subtracted with this value."""

    shift_y: float
    """float: Value to shift the y-coordinates with. All y-coordinates will be subtracted with this value."""
    
class Variable(BaseModel):
    """Configuration properties of a variable."""

    name: str
    """str: The name of the NetCDF variable"""

    color: Color
    """Color: The vertex color in the mesh defined by the normalized red, green, blue and alpha (RGBA) values."""

    metallic_factor: float
    """float: The metallic factor determines the degree of metallicity or non-metallicity of the mesh material. A value of 0.0 represents a non-metallic surface, while a value of 1.0 indicates a fully metallic surface."""

    roughness_factor: float
    """float: The roughness factor defines the smoothness or roughness of the mesh material. A roughness value of 0.0 represents a perfectly smooth surface with sharp reflections, while a value of 1.0 indicates a completely rough surface with scattered reflections."""

    use_threshold: bool
    """bool: Whether or not to add a threshold mesh to filter values below the threshold height."""

    threshold_color: Optional[Color]
    """Optional[Color]: The vertex color in the threshold mesh defined by the normalized red, green, blue and alpha (RGBA) values."""

    threshold_height: Optional[float]
    """Optional[float]: The height (vertex z-values) of the threshold mesh."""

    @root_validator
    def validate_threshold(cls, values: Dict[str, Any]):
        def validate_required(field: str):
            field_value = values.get(field)
            if field_value is None:
                raise ValueError(f"'{field}' is required when 'use_threshold' is true.")

        if values["use_threshold"]:
            validate_required("threshold_color")
            validate_required("threshold_height")

        return values

    @validator("color", "threshold_color")
    def validate_color(cls, color: Color) -> Color:
        """Validate a color. The color should be a list that contains 4 floating values between 0.0 and 1.0 (inclusive)."""

        if color is None:
            return color

        if len(color) != 4:
            msg = "A color should be defined as a list of 4 floating values: the normalized red, green, blue and alpha (RGBA) values."
            raise ValueError(msg)

        for channel in color:
            if not in_range(channel, 0.0, 1.0):
                msg = f"The color channel {channel} is outside of range 0.0-1.0. A color should be defined by the normalized red, green, blue and alpha (RGBA) values."
                raise ValueError(msg)

        return color

    @validator("metallic_factor", "roughness_factor")
    def validate_in_range(cls, value: float) -> float:
        if not in_range(value, 0.0, 1.0):
            msg = "Value must be between 0.0 and 1.0"
            raise ValueError(msg)

        return value


class Config(AbstractJsonConfigFile, AbstractFileVersionFile):
    """The configuration settings described in the configuration JSON file."""

    _expected_file_version = Version("0.1.0")

    model_type: ModelType
    """ModelType: The model type that is used for the input."""
    
    time_index_start: int
    """int: The time index the animation should start with."""

    time_index_end: Optional[int]
    """Optional[int]: The time index the animation should end with. Will default to the index of the last time step of the model."""

    times_per_frame: int
    """int: The number of time steps per animation frame."""

    shift_coordinates: Optional[Union[str, CrsShifting]]
    """Optional[Union[str, CrsShifting]]: The options how to shift the x- and y-coordinates. Typically used to create a reference point, such that an x and y become the origin (0,0)."""

    scale_horizontal: float
    """float: The horizontal scaling factor of the mesh coordinates compared to the coordinates from file."""

    scale_vertical: float
    """float: The vertical scaling factor of the mesh coordinates compared to the coordinates from file."""

    variables: List[Variable]
    """List[Variable]: List of configuration of the variables that should be converted to glTF."""

    crs_transformation: Optional[CrsTransformation]
    """Optional[CrsTransformation]: The configuration settings for transforming the coordinates to  different coordinate system."""