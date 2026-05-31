import shutil
from pathlib import Path

missed = "missing.png"
folder = Path("~/hobby/collection/scans/gum_wrappers/kent/power/148-259/inner")
numbers = range(148, 259)

if __name__ == "__main__":
    for number in numbers:
        shutil.copyfile(missed, folder / f"{number}.0.png")
