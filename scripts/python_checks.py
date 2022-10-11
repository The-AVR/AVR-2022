import argparse
import os
import shutil
import subprocess
import sys
from typing import List

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def main(directory: str, checks: List[str]) -> None:
    directory = os.path.abspath(directory)

    exit_codes: List[int] = []

    for check in checks:
        cmd = None

        if check == "black":
            cmd = [sys.executable, "-m", "black", directory, "--check"]
        elif check == "isort":
            cmd = [sys.executable, "-m", "isort", directory, "--check"]
        elif check == "autoflake":
            cmd = [
                sys.executable,
                "-m",
                "autoflake",
                directory,
                "--check",
            ]
        elif check == "pyleft":
            cmd = [sys.executable, "-m", "pyleft", directory]
        elif check == "pyright":
            cmd = [shutil.which("npx"), "pyright", directory, "--verbose"]
        elif check == "pflake8":
            cmd = [sys.executable, "-m", "pflake8", directory]

        if cmd is None:
            raise ValueError(f"Invalid check {check}")

        cmd_combined = " ".join(cmd)
        print("=" * len(cmd_combined))
        print(cmd_combined)
        exit_codes.append(subprocess.run(cmd, cwd=ROOT).returncode)

    sys.exit(int(any(exit_codes)))


if __name__ == "__main__":
    checks = ["black", "isort", "autoflake", "pyleft", "pyright", "pflake8"]

    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=str, help="Directory to run in")
    parser.add_argument(
        "checks", nargs="*", default=checks, help="Checks to run. Defaults to all"
    )

    args = parser.parse_args()

    if any(c not in checks for c in args.checks):
        parser.error("Invalid check selected")

    main(args.directory, args.checks)
