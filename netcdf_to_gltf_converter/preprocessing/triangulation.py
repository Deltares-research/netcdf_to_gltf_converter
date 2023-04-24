import xugrid as xu

class Triangulator:
    """Class to triangulate grid cells within a xu.Ugrid2d."""
    
    @staticmethod
    def triangulate(ugrid2d: xu.Ugrid2d):
        """Triangulate the provided UGrid 2D.

        Args:
            ugrid2d (xu.Ugrid2d): The UGrid 2D to triangulate.

        Returns:
            xu.Ugrid2d: The triangulated UGrid 2D.
        """
        return ugrid2d.triangulate()
        
        