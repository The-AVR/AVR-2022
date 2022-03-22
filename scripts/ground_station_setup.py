import subprocess
import sys
from pathlib import Path


def main() -> None:
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "wheel", "pip", "--upgrade"],
        check=True,
    )

    # Get the base directory
    basepath = Path(__file__).parent.parent

    # Get the top level directories
    directories = basepath.glob("*")

    # skip directories that start with a dot
    for directory in directories:
        if directory.name.startswith("."):
            continue

        # Install requirements.txt recursively
        for filepath in directory.glob("**/ground_station_requirements*.txt"):
            print(f" ----- Installing {filepath.absolute()} ----- ")
            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pip",
                    "install",
                    "-r",
                    str(filepath.absolute()),
                ],
                check=True,
            )


if __name__ == "__main__":
    main()
