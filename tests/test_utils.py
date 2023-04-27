import numpy as np
import pytest

from netcdf_to_gltf_converter.utils import validate_2d_array


def test_validate_2d_array_with_unexpected_shape_raises_assertion_error():
    array = np.array([1, 2, 3], dtype="float32")
    with pytest.raises(AssertionError):
        validate_2d_array(array, "float32", 1)


def test_validate_2d_array_with_unexpected_dtype_raises_assertion_error():
    array = np.array([[1, 2], [3, 4]], dtype="uint32")
    with pytest.raises(AssertionError):
        validate_2d_array(array, "float32", 2)


def test_validate_2d_array_with_unexpected_number_of_columns_raises_assertion_error():
    array = np.array([[1, 2], [3, 4]], dtype="float32")
    with pytest.raises(AssertionError):
        validate_2d_array(array, "float32", 3)


def test_validate_2d_array_with_correct_array_does_not_raise_any_error():
    array = np.array([[1, 2], [3, 4]], dtype="float32")
    validate_2d_array(array, "float32", 2)
