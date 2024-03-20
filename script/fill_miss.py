import shutil
from pathlib import Path

missed = "../missing.png"
folder = Path("../gum_wrappers/kent/turbo/sport/401-470/inner")
numbers = range(401, 471)

if __name__ == "__main__":
    for number in numbers:
        shutil.copyfile(missed, folder / f"{number}.0.png")
