import filecmp
from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Generator

resources = Path("tests") / "resources"
dhydro_resources = resources / "d-hydro"
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


@contextmanager
def get_temp_file(filename: str) -> Generator[Path, None, None]:
    """Gets a path to a file in a temporary directory with the specified file name.
    Args:
        filename (str): The file name.
    Example:
        >>>     with get_temp_file("some_file_name") as temp_file:
        >>>         print(f"Do something with {temp_file}")
    Yields:
        Generator[Path, None, None]: Generator with the path to the file in the temporary directory as yield type.
    """
    with TemporaryDirectory() as temp_dir:
        yield Path(temp_dir, filename)
