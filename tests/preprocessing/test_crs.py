from pyproj import CRS

from netcdf_to_gltf_converter.preprocessing.crs import (create_crs,
                                                        create_crs_transformer)


def test_create_crs_transformer():
    source_epsg = 4979
    target_epsg = 7415

    source_crs = create_crs(source_epsg)
    target_crs = create_crs(target_epsg)

    transformer = create_crs_transformer(source_crs, target_crs)

    assert transformer is not None
    assert transformer.is_network_enabled == True
    assert (
        transformer.source_crs.name
        == "WGS 84 (with axis order normalized for visualization)"
    )
    assert transformer.target_crs.name == "Amersfoort / RD New + NAP height"


def test_create_crs():
    epsg = 7415

    crs = create_crs(epsg)

    assert isinstance(crs, CRS)
    assert crs.name == "Amersfoort / RD New + NAP height"
