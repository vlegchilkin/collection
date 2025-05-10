import os
from pathlib import Path

from PIL import Image

SIZE = (320, 240)

ROOT = Path("..")
SCANS_DIR = Path("../scans")


def build(root_dir: str):
    output_dir = Path(root_dir) / "thumbnails"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print("thumbnails dir created")
    else:
        for t_root, t_dirs, t_files in os.walk(output_dir):
            for filename in t_files:
                if filename != "missed.png" and filename.endswith(".png"):
                    os.remove(os.path.join(t_root, filename))

    for original in ["inner", "outer"]:
        os.makedirs(output_dir / original, exist_ok=True)
        out_root = output_dir / original
        scan_path = SCANS_DIR / root_dir[len(str(ROOT)) + 1:] / original
        for t_root, t_dirs, t_files in os.walk(scan_path):
            x_path = Path(t_root).relative_to(scan_path)
            for dirname in t_dirs:
                os.makedirs(out_root / x_path / dirname, exist_ok=True)
            file_root = out_root / x_path
            for filename in t_files:
                if filename.endswith(".png"):
                    full_path = Path(t_root) / filename
                    img = Image.open(full_path)
                    img.thumbnail(SIZE)
                    img.save(os.path.join(file_root, filename))


if __name__ == "__main__":
    for root, dirs, files in os.walk(f"../gum_wrappers/kent/turbo/super/331-400"):
        if "thumbnails" in dirs:
            build(root)
