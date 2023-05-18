from pathlib import Path

from pygltflib import GLTF2


class Exporter:
    def export(self, gltf: GLTF2, file_path: Path):
        """Export the GLTF object to file.

        If a file at the provided path already exists, it will be overwritten.

        Args:
            gltf (GLTF2): The GLTF object to export.
            file_path (Path): The file path to export to.

        Raises:
            ValueError: When the file extension is not .gltf or .glb.
        """
        file_extension = file_path.suffix.lower()
        if file_extension == ".gltf":
            gltf.save(file_path)
        elif file_extension == ".glb":
            gltf.save_binary(file_path)
        else:
            raise ValueError(
                f"GLTF file cannot be exported: unsupported file type '{file_path.suffix}'. Supported: .gltf, .glb"
            )
