import subprocess
import sys
import os
import shutil

THIS_DIR = os.path.abspath(os.path.dirname(__file__))

if __name__ == "__main__":
    # install npm packages
    npm = shutil.which("npm")
    assert npm is not None
    subprocess.check_call([npm, "install"], cwd=THIS_DIR)

    # install python packages
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "pip", "wheel", "--upgrade"]
    )
    subprocess.check_call(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "-r",
            os.path.join(THIS_DIR, "requirements.txt"),
        ]
    )
