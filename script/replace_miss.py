import os
import shutil
from pathlib import Path


def replace(missing_filepath: Path, inner_path: Path):
    for filename in os.listdir(inner_path):
        if filename.endswith(".0.png"):
            shutil.copyfile(missing_filepath, inner_path / filename)


if __name__ == "__main__":
    missing_file = None
    for root, dirs, files in os.walk(".."):
        if "missing.png" in files:
            missing_file = Path(root) / "missing.png"
        if "inner" in dirs:
            replace(missing_file, Path(root) / "inner")
