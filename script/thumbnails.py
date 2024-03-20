import os
from pathlib import Path

from PIL import Image

SIZE = (200, 150)


def build(root_dir: str):
    output_dir = Path(root_dir) / "thumbnails"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print("thumbnails dir created")
    else:
        for t_root, t_dirs, t_files in os.walk(output_dir):
            for filename in t_files:
                if filename.endswith(".png"):
                    os.remove(os.path.join(t_root, filename))

    for original in ["inner", "outer"]:
        os.makedirs(output_dir / original, exist_ok=True)
        for filename in os.listdir(os.path.join(root_dir, original)):
            if filename.endswith(".png"):
                full_path = os.path.join(root_dir, original, filename)
                img = Image.open(full_path)
                img.thumbnail(SIZE)
                img.save(os.path.join(output_dir, original, filename))


if __name__ == "__main__":
    for root, dirs, files in os.walk("../gum_wrappers/kent/turbo/black/51-120"):
        if "thumbnails" in dirs:
            build(root)
