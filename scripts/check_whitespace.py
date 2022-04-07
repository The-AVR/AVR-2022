import os
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
EXCLUDED_EXTENSIONS = [".patch", ".hex", ".pdf", ".step"]


def main() -> None:
    # get a list of text files tracked by git
    filenames = (
        subprocess.check_output(["git", "grep", "-I", "-l", "."], cwd=ROOT)
        .decode("utf-8")
        .strip()
        .splitlines()
    )

    found = False

    for filename in filenames:
        # skip excluded file types
        if any(filename.lower().endswith(ext) for ext in EXCLUDED_EXTENSIONS):
            continue

        # open each file
        with open(os.path.join(ROOT, filename), "r", encoding="utf-8") as fp:
            for i, line in enumerate(fp.readlines()):
                # remove the newline characters
                t = line.strip("\n\r")
                # see if there is any whitespace left
                if t.endswith(" ") or t.endswith("\t"):
                    found = True
                    print(f"{filename}:{i+1}")

    sys.exit(int(found))


if __name__ == "__main__":
    main()
