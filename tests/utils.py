import filecmp
from pathlib import Path

resources = Path("tests") / "resources"
dhydro_resources = resources / "d-hydro"
xbeach_resources = resources / "xbeach"
reference_files = resources / "reference"


def assert_files_equal(file_1: Path, file_2: Path):
    """Assert whether the contents of two files are equal.

    Args:
        file_1 (Path): The path of the first file.
        file_2 (Path): The path of the second file.

    Raises:
        AssertionError: When the content of the two files are not equal.
    """
    assert filecmp.cmp(str(file_1), str(file_2)) == True