import pyproj
import pyproj.network


def create_crs_transformer(source_epsg: int, target_epsg: int) -> pyproj.Transformer:
    """Create a coordinate transformer that transforms the coordinates from a source coordinate system to a target coordinate system.
    
    Args:
        source_epsg (int): The EPSG code of the source coordinate system.
        target_epsg (int): The EPSG code of the target coordinate system.

    Returns:
        pyproj.Transformer: The coordinate transformer
    """
    pyproj.network.set_network_enabled(True)
    
    source_crs = pyproj.CRS.from_epsg(source_epsg)
    target_crs = pyproj.CRS.from_epsg(target_epsg)
    
    transformer = pyproj.Transformer.from_crs(
        crs_from=source_crs, crs_to=target_crs, always_xy=True
    )
    return transformer