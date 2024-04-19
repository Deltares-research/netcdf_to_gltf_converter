from netcdf_to_gltf_converter.config import CrsTransformation


class TestCrsTransformation():
    def test_construction_with_epsg_integers(self):
        source_epsg = 4979
        target_epsg = 7415
        
        crs_transformation = CrsTransformation(source_epsg=source_epsg, 
                                               target_epsg=target_epsg)
        
        assert crs_transformation.source_epsg.name == 'WGS 84'
        assert crs_transformation.target_epsg.name == 'Amersfoort / RD New + NAP height'
        
    def test_construction_with_epsg_strings(self):
        source_epsg = '4979'
        target_epsg = '7415'
        
        crs_transformation = CrsTransformation(source_epsg=source_epsg, 
                                               target_epsg=target_epsg)
        
        assert crs_transformation.source_epsg.name == 'WGS 84'
        assert crs_transformation.target_epsg.name == 'Amersfoort / RD New + NAP height'