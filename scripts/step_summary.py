import os
import subprocess
import sys

command = os.environ['RUN_CMD'].split()

print(f"Running: \033[0;36m{' '.join(command)}\033[0m")

process = subprocess.run(command)

if process.returncode != 0:
    with open(os.environ["GITHUB_STEP_SUMMARY"], 'w') as fp:
        fp.write(os.environ["CMD_FAILURE_TEXT"])

sys.exit(process.returncode)
