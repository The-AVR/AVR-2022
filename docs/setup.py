import os
import shutil
import subprocess
import sys

THIS_DIR = os.path.abspath(os.path.dirname(__file__))

if __name__ == "__main__":
    # install npm packages
    npm = shutil.which("npm")
    assert npm is not None
    subprocess.check_call([npm, "install"], cwd=THIS_DIR)

    # install python packages
    subprocess.check_call(
        [
            sys.executable,
            os.path.join(THIS_DIR, "..", "scripts", "install_requirements.py"),
            "--directory",
            THIS_DIR,
            "--strict",
        ]
    )
