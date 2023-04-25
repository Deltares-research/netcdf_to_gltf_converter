from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Generator

test_data = Path("tests") / "data"


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
