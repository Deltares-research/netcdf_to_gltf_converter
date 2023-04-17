import argparse
from pathlib import Path

def get_args():
    """Parses and returns the arguments"""
    parser = argparse.ArgumentParser()
    parser.add_argument("netcdf", help="Path to the source NetCDF file")
    parser.add_argument("gltf", help="Path to the destination glTF file")

    return parser.parse_args()

if __name__ == "__main__":
    args = get_args()
    netcdf = Path(args.netcdf)
    gltf = Path(args.gltf)
