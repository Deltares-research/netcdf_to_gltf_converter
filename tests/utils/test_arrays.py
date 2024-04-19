import numpy as np
import pytest

from netcdf_to_gltf_converter.utils.arrays import (float32_array, uint32_array,
                                                   validate_2d_array)


def test_validate_2d_array_with_unexpected_shape_raises_assertion_error():
    array = np.array([1, 2, 3], dtype=np.float32)
    with pytest.raises(AssertionError):
        validate_2d_array(array, np.float32, 1)


def test_validate_2d_array_with_unexpected_dtype_raises_assertion_error():
    array = np.array([[1, 2], [3, 4]], dtype=np.uint32)
    with pytest.raises(AssertionError):
        validate_2d_array(array, np.float32, 2)


def test_validate_2d_array_with_unexpected_number_of_columns_raises_assertion_error():
    array = np.array([[1, 2], [3, 4]], dtype=np.float32)
    with pytest.raises(AssertionError):
        validate_2d_array(array, np.float32, 3)


def test_validate_2d_array_with_correct_array_does_not_raise_any_error():
    array = np.array([[1, 2], [3, 4]], dtype=np.float32)
    validate_2d_array(array, np.float32, 2)


def test_float32_array():
    data = [1, 2, 3]

    array = float32_array(data)

    assert array.tolist() == data
    assert array.dtype == np.float32


def test_uint32_array():
    data = [1, 2, 3]

    array = uint32_array(data)

    assert array.tolist() == data
    assert array.dtype == np.uint32
