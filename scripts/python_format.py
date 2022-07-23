import argparse
import os
import subprocess
import sys
from typing import List

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def main(directory: str, formatters: List[str]) -> None:
    directory = os.path.abspath(directory)

    for formatter in formatters:
        cmd = None

        if formatter == "black":
            cmd = [sys.executable, "-m", "black", directory]
        elif formatter == "isort":
            cmd = [sys.executable, "-m", "isort", directory]
        elif formatter == "autoflake":
            cmd = [
                sys.executable,
                "-m",
                "autoflake",
                "--recursive",
                "--in-place",
                "--remove-all-unused-imports",
                directory,
            ]

        if cmd is None:
            raise ValueError(f"Invalid formatter {formatter}")

        cmd_combined = " ".join(cmd)
        print("=" * len(cmd_combined))
        print(cmd_combined)
        subprocess.check_call(cmd, cwd=ROOT)


if __name__ == "__main__":
    formatters = ["black", "isort", "autoflake"]

    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=str, help="Directory to run in")
    parser.add_argument(
        "formatters",
        nargs="*",
        default=formatters,
        help="Formatters to run. Defaults to all",
    )

    args = parser.parse_args()

    if any(f not in formatters for f in args.formatters):
        parser.error("Invalid formatter selected")

    main(args.directory, args.formatters)
