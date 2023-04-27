import numpy as np


def validate_2d_array(array: np.ndarray, dtype: str, n_col: int):
    """Validate the 2D array with the provided expectations.

    Args:
        array (np.ndarray): The 2D array to validate.
        dtype (str): The expected data type.
        n_col (int): The expected number of columns in the array.
        
    Raises:
        AssertionError: When the shape or dtype of the array does not match the expectations.
    """
    
    assert array.dtype == dtype
    assert len(array.shape) == 2
    assert array.shape[1] == n_col