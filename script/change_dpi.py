import os
from pathlib import Path

from PIL import Image

folder = Path("../gum_wrappers/kent/turbo/super/331-400/inner")

if __name__ == "__main__":
    for filename in os.listdir(folder):
        if not filename.endswith("331.5.png"):
            continue
        img = Image.open(folder / filename)
        if img.width < 1000:
            continue
        (width, height) = [int(s / 2) for s in img.size]
        image_resized = img.resize((width, height), Image.LANCZOS)
        image_resized.save(folder / "out" / filename)
