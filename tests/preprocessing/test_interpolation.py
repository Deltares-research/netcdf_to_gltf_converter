import numpy as np

from netcdf_to_gltf_converter.preprocessing.interpolation import Interpolator, Location
from tests.preprocessing.utils import Factory


class TestInterpolator:
    def test_interpolate_nearest(self):
        data_coords = np.array(
            [[0.75, 0.25], [1.75, 0.75], [0.25, 1.25], [1.25, 1.75]], dtype="float32"
        )
        data_values = np.array([1, 2, 3, 4], dtype="float32")
        grid = Factory.create_rectilinear_ugrid2d()
        location = Location.nodes

        interpolated_values = Interpolator.interpolate_nearest(
            data_coords, data_values, grid, location
        )

        exp_interpolated_values = [
            [0, 0, 1],
            [1, 0, 1],
            [2, 0, 2],
            [0, 1, 3],
            [1, 1, 1],
            [2, 1, 2],
            [0, 2, 3],
            [1, 2, 4],
            [2, 2, 4],
        ]

        assert np.array_equal(interpolated_values, exp_interpolated_values)

    def test_interpolate_linear(self):
        data_coords = np.array(
            [[1.0, 0.5], [2.0, 1.0], [1.0, 2.0], [0.5, 1.0]], dtype="float32"
        )
        data_values = np.array([1, 2, 3, 4], dtype="float32")
        grid = Factory.create_rectilinear_ugrid2d()
        location = Location.nodes

        interpolated_values = Interpolator.interpolate_linear(
            data_coords, data_values, grid, location
        )

        exp_interpolated_values = [
            [0, 0, float("nan")],
            [1, 0, float("nan")],
            [2, 0, float("nan")],
            [0, 1, float("nan")],
            [1, 1, 1.6666666666666665],
            [2, 1, 2.0],
            [0, 2, float("nan")],
            [1, 2, 3.0],
            [2, 2, float("nan")],
        ]

        assert np.array_equal(
            interpolated_values, exp_interpolated_values, equal_nan=True
        )
