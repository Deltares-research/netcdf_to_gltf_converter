import numpy as np

from netcdf_to_gltf_converter.interpolation.interpolator import Interpolator


class TestInterpolator:
    def test_interpolate_nearest(self):
        data_points = np.array(
            [[0.75, 0.25], [1.74, 0.75], [0.25, 1.25], [1.25, 1.175]], dtype="float32"
        )
        data_values = np.array([1, 2, 3, 4], dtype="float32")
        points_to_interpolate = np.array(
            [[0, 0], [1, 0], [2, 0], [0, 1], [1, 1], [2, 1], [0, 2], [1, 2], [2, 2]],
            dtype="float32",
        )

        interpolated_values = Interpolator.interpolate_nearest(
            data_points, data_values, points_to_interpolate
        )

        exp_interpolated_values = [1, 1, 2, 3, 4, 2, 3, 4, 4]

        assert np.array_equal(interpolated_values, exp_interpolated_values)

    def test_interpolate_linear(self):
        data_points = np.array(
            [[1.0, 0.5], [2.0, 1.0], [1.0, 2.0], [0.5, 1.0]], dtype="float32"
        )
        data_values = np.array([1, 2, 3, 4], dtype="float32")
        points_to_interpolate = np.array(
            [[0, 0], [1, 0], [2, 0], [0, 1], [1, 1], [2, 1], [0, 2], [1, 2], [2, 2]],
            dtype="float32",
        )

        interpolated_values = Interpolator.interpolate_linear(
            data_points, data_values, points_to_interpolate
        )

        exp_interpolated_values = [
            float("nan"),
            float("nan"),
            float("nan"),
            float("nan"),
            1.6666666666666665,
            2.0,
            float("nan"),
            3.0,
            float("nan"),
        ]

        assert np.array_equal(
            interpolated_values, exp_interpolated_values, equal_nan=True
        )
