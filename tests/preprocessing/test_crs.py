from netcdf_to_gltf_converter.preprocessing.crs import create_crs_transformer


def test_create_crs_transformer():
    transformer = create_crs_transformer(source_epsg=4979, target_epsg=7415)
    
    assert transformer is not None
    assert transformer.is_network_enabled == True
    assert transformer.source_crs.name == 'WGS 84 (with axis order normalized for visualization)'
    assert transformer.target_crs.name == 'Amersfoort / RD New + NAP height'