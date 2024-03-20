import os
from pathlib import Path

folder = Path("../gum_wrappers/kent/oto-moto/101-200/inner")

if __name__ == "__main__":
    for filename in os.listdir(folder):
        if not filename.endswith(".png"):
            continue
        os.rename(folder / filename, folder / f"{filename[:-4]}.4.png")
