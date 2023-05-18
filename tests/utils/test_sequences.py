from netcdf_to_gltf_converter.utils.sequences import inclusive_range

def test_inclusive_range_with_stop_value_included_in_step_increments():
    result = inclusive_range(0, 12, 3)
    expected = [0, 3, 6, 9, 12]
    assert result == expected

def test_inclusive_range_with_stop_value_not_included_in_step_increments():
    result = inclusive_range(3, 21, 5)
    expected = [3, 8, 13, 18, 21]
    assert result == expected