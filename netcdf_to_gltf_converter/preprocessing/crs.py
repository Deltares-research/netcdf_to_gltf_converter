import pyproj
import pyproj.network
from pyproj.crs import CRS


def create_crs_transformer(source_crs: CRS, target_crs: CRS) -> pyproj.Transformer:
    """Create a coordinate transformer that transforms the coordinates from a source coordinate system to a target coordinate system.
    
    Args:
        source_epsg (CRS): The source coordinate system.
        target_epsg (CRS): The target coordinate system.

    Returns:
        pyproj.Transformer: The coordinate transformer
    """
    pyproj.network.set_network_enabled(True)
    
    transformer = pyproj.Transformer.from_crs(
        crs_from=source_crs, crs_to=target_crs, always_xy=True
    )
    return transformer

def create_crs(epsg: int) -> CRS:
    """Create a coordinate system from the given EPSG code. 

    Args:
        epsg (int): The EPSG code to create the coordinate system from.

    Returns:
        CRS: The created coordinate system.
    """
    return CRS.from_epsg(epsg)