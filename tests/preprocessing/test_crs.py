from pyproj import CRS
from pyproj.crs import CompoundCRS

from netcdf_to_gltf_converter.preprocessing.crs import (create_compound_crs,
                                                        create_crs,
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


def test_create_compound_crs():
    epsg_horizontal = 32617
    epsg_vertical = 5703

    crs = create_compound_crs(epsg_horizontal, epsg_vertical)

    assert isinstance(crs, CompoundCRS)
    assert crs.name == "WGS 84 / UTM zone 17N + NAVD88 height"
    assert crs.is_compound == True
