import argparse
import os
import subprocess
import sys
from pathlib import Path


def main(directory: str, strict: bool = False) -> None:
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "wheel", "pip", "--upgrade"],
        check=True,
    )

    # Install requirements.txt recursively
    for filepath in Path(directory).glob("**/requirements*.txt"):
        # don't install any requirements.txt files that may be in the virtual env
        # or in the PX4 temp directory
        if ".venv" in str(filepath):
            continue

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
            check=strict,
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--directory",
        "-d",
        type=str,
        default=os.path.join(os.path.dirname(__file__), ".."),
        help="Directory to walk. Defaults to repo root",
    )
    parser.add_argument(
        "--strict",
        "-s",
        action="store_true",
        help="Fail if requirements.txt could not installed",
    )

    args = parser.parse_args()
    args.directory = os.path.abspath(args.directory)

    main(args.directory, args.strict)
