import os
import subprocess
import sys

THIS_DIR = os.path.abspath(os.path.dirname(__file__))

if __name__ == "__main__":
    queue_dir = os.path.join(THIS_DIR, "libraries", "Queue")

    # apply patch
    subprocess.check_call(["git", "reset", "--hard"], cwd=queue_dir)
    subprocess.check_call(
        [
            "git",
            "apply",
            "--ignore-whitespace",
            "--verbose",
            os.path.join(THIS_DIR, "libraries", "queue-default.patch"),
        ],
        cwd=queue_dir,
    )
    subprocess.check_call(
        [
            "git",
            "update-index",
            "--assume-unchanged",
            os.path.join("src", "cppQueue.h"),
        ],
        cwd=queue_dir,
    )

    # install platformio
    subprocess.check_call(
        [
            sys.executable,
            os.path.join(THIS_DIR, "..", "scripts", "install_requirements.py"),
            "--directory",
            THIS_DIR,
            "--strict",
        ]
    )
