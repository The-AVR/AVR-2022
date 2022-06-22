import os
import subprocess

THIS_DIR = os.path.abspath(os.path.dirname(__file__))

cmd = [
    "pyinstaller",
    os.path.join(THIS_DIR, "app.py"),
    "--onefile",
    "--noconfirm",
    "--name",
    f"AVRGUI.{subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD'], text=True).strip()}",
    "--icon",
    os.path.join(THIS_DIR, "lib", "img", "logo.ico"),
    "--add-data",
    f"{os.path.join(THIS_DIR, 'lib', 'img')}{os.pathsep}{os.path.join('lib', 'img')}",
]

print(cmd)
subprocess.check_call(cmd, cwd=THIS_DIR)
