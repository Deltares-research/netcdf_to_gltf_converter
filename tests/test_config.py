from pyproj.crs import CompoundCRS

from netcdf_to_gltf_converter.config import CrsTransformation


class TestCrsTransformation:
    def test_construction_with_epsg_integers(self):
        source_epsg = 4979
        target_epsg = 7415

        crs_transformation = CrsTransformation(
            source_crs=source_epsg, target_crs=target_epsg
        )

        assert crs_transformation.source_crs.name == "WGS 84"
        assert crs_transformation.target_crs.name == "Amersfoort / RD New + NAP height"

    def test_construction_with_epsg_strings(self):
        source_epsg = "4979"
        target_epsg = "7415"

        crs_transformation = CrsTransformation(
            source_crs=source_epsg, target_crs=target_epsg
        )

        assert crs_transformation.source_crs.name == "WGS 84"
        assert crs_transformation.target_crs.name == "Amersfoort / RD New + NAP height"

    def test_construction_with_compound_epsg_strings(self):
        source_epsg = "4326+5773"
        target_epsg = "32617+5703"

        crs_transformation = CrsTransformation(
            source_crs=source_epsg, target_crs=target_epsg
        )

        assert crs_transformation.source_crs.name == "WGS 84 + EGM96 height"
        assert isinstance(crs_transformation.source_crs, CompoundCRS)
        assert (
            crs_transformation.target_crs.name
            == "WGS 84 / UTM zone 17N + NAVD88 height"
        )
        assert isinstance(crs_transformation.target_crs, CompoundCRS)
