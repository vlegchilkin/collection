import os
from pathlib import Path
from PIL import Image

folder = Path("../gum_wrappers/kent/turbo/sport/401-470/inner")

if __name__ == "__main__":
    for filename in os.listdir(folder):
        if not filename.endswith(".jpeg"):
            continue
        img = Image.open(folder / filename)
        img = img.convert('L')  # convert image to black and white
        img.save(folder / "out" / f"{filename[:-4]}png")
