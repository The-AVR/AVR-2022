import argparse
import os
import platform
import shutil
import subprocess
import sys
from typing import List

# warning, v1.10.2 does not appear to build anymore
PX4_VERSION = "v1.12.3"

THIS_DIR = os.path.abspath(os.path.dirname(__file__))
DIST_DIR = os.path.join(THIS_DIR, "dist")

PX4_DIR = os.path.join(THIS_DIR, "build", "PX4-Autopilot")

if PX4_VERSION < "v1.13.0":
    PYMAVLINK_DIR = os.path.join(THIS_DIR, "build", "pymavlink")
else:
    PYMAVLINK_DIR = os.path.join(
        PX4_DIR,
        "src",
        "modules",
        "mavlink",
        "mavlink",
        "pymavlink",
    )


def print2(msg: str) -> None:
    print(f"--- {msg}", flush=True)


def clean_directory(directory: str, line_endings: List[str]) -> None:
    # cancel if the directory is not already there
    if not os.path.isdir(directory):
        return

    for filename in os.listdir(directory):
        if any(filename.endswith(e) for e in line_endings):
            os.remove(os.path.join(directory, filename))


def clone_pymavlink() -> None:
    if os.path.isdir(PYMAVLINK_DIR):
        # update the checkout if we already have it
        print2("Updating pymavlink")
        subprocess.check_call(["git", "pull"], cwd=PYMAVLINK_DIR)

    else:
        # clone fresh
        print2("Cloning pymavlink")
        subprocess.check_call(
            ["git", "clone", "https://github.com/ardupilot/pymavlink", PYMAVLINK_DIR]
        )


def clone_px4() -> None:
    if os.path.isdir(PX4_DIR):
        # reset checkout if we already have it
        # this will fail on PX4 version changes
        print2("Resetting PX4 checkout")
        subprocess.check_call(["git", "fetch", "origin"], cwd=PX4_DIR)
        subprocess.check_call(["git", "checkout", PX4_VERSION], cwd=PX4_DIR)
        subprocess.check_call(["git", "reset", "--hard", PX4_VERSION], cwd=PX4_DIR)
        subprocess.check_call(["git", "pull", "--recurse-submodules"], cwd=PX4_DIR)
    else:
        # clone fresh
        print2("Cloning PX4")
        subprocess.check_call(
            [
                "git",
                "clone",
                "https://github.com/PX4/PX4-Autopilot",
                PX4_DIR,
                "--depth",
                "1",
                "--branch",
                PX4_VERSION,
                "--recurse-submodules",
            ]
        )

    print2("Applying PX4 patch")
    subprocess.check_call(
        [
            "git",
            "apply",
            "--ignore-space-change",
            "--ignore-whitespace",
            os.path.join(THIS_DIR, "patches", f"hil_gps_heading_{PX4_VERSION}.patch"),
        ],
        cwd=PX4_DIR,
    )


def container(build_pymavlink: bool, build_px4: bool, git_hash: str) -> None:
    # code that runs inside the container
    if PX4_VERSION < "v1.13.0":
        clone_pymavlink()

    clone_px4()

    print2("Installing Python dependencies")
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "--upgrade", "pip", "wheel"]
    )
    subprocess.check_call(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "-r",
            os.path.join(PYMAVLINK_DIR, "requirements.txt"),
        ]
    )

    # build directory paths
    if PX4_VERSION < "v1.13.0":
        message_definitions_dir = os.path.join(
            PX4_DIR,
            "mavlink",
            "include",
            "mavlink",
            "v2.0",
            "message_definitions",
        )
        generated_message_dir = os.path.join(message_definitions_dir, "..")
    else:
        message_definitions_dir = os.path.join(
            PX4_DIR,
            "src",
            "modules",
            "mavlink",
            "mavlink",
            "message_definitions",
            "v1.0",
        )
        generated_message_dir = os.path.join(message_definitions_dir, "..", "..", "..")

    bell_xml_def = os.path.join(message_definitions_dir, "bell.xml")

    print2("Injecting Bell MAVLink message")
    shutil.copyfile(os.path.join(THIS_DIR, "bell.xml"), bell_xml_def)

    # generate the mavlink C code
    if PX4_VERSION < "v1.13.0":
        subprocess.check_call(
            [
                sys.executable,
                "-m",
                "pymavlink.tools.mavgen",
                "--lang=C",
                "--wire-protocol=2.0",
                f"--output={generated_message_dir}",
                bell_xml_def,
            ],
            cwd=os.path.join(PYMAVLINK_DIR, ".."),
        )

    # changes need to be committed to build
    # git config does not matter, just need *something* to commit
    subprocess.check_call(
        ["git", "config", "user.email", "github-bot@bellflight.com"], cwd=PX4_DIR
    )
    subprocess.check_call(["git", "config", "user.name", "Github Actions"], cwd=PX4_DIR)
    subprocess.check_call(["git", "add", "."], cwd=PX4_DIR)
    subprocess.check_call(
        ["git", "commit", "-m", "Local commit to facilitate build"], cwd=PX4_DIR
    )

    if build_pymavlink:
        print2("Generating pymavlink package")

        # copy message definitions from px4 so we're using the exact same version
        shutil.rmtree(
            os.path.join(PYMAVLINK_DIR, "message_definitions", "v1.0"),
            ignore_errors=True,
        )
        shutil.copytree(
            message_definitions_dir,
            os.path.join(PYMAVLINK_DIR, "message_definitions", "v1.0"),
        )

        pymavlink_dist_dir = os.path.join(PYMAVLINK_DIR, "dist")

        # clean the pymavlink build and target dirs
        clean_directory(pymavlink_dist_dir, [".tar.gz", ".whl"])
        clean_directory(DIST_DIR, [".tar.gz", ".whl"])

        # make a new environment with the mavlink dialect set
        new_env = os.environ.copy()
        new_env["MAVLINK_DIALECT"] = "bell"
        subprocess.check_call(
            [sys.executable, "setup.py", "sdist", "bdist_wheel"],
            cwd=PYMAVLINK_DIR,
            env=new_env,
        )

        # copy the outputs to the target directory
        for filename in os.listdir(pymavlink_dist_dir):
            shutil.copyfile(
                os.path.join(pymavlink_dist_dir, filename),
                os.path.join(DIST_DIR, filename),
            )

        # generate lua plugins for Wireshark
        # https://mavlink.io/en/guide/wireshark.html
        subprocess.check_call(
            [
                sys.executable,
                "-m",
                "pymavlink.tools.mavgen",
                "--lang=WLua",
                "--wire-protocol=2.0",
                f"--output={os.path.join(DIST_DIR, 'bell.lua')}",
                bell_xml_def,
            ],
            cwd=os.path.join(PYMAVLINK_DIR, ".."),
        )

    if build_px4:
        print2("Building PX4 firmware")

        px4_build_dir = os.path.join(PX4_DIR, "build")

        # clean the PX4 build and target dir
        clean_directory(px4_build_dir, [".px4"])
        clean_directory(DIST_DIR, [".px4"])

        # pixhawk v5X and NXP
        targets = ["px4_fmu-v5x_default", "nxp_fmuk66-v3_default"]
        for target in targets:
            subprocess.check_call(["make", target, "-j"], cwd=PX4_DIR)
            shutil.copyfile(
                os.path.join(px4_build_dir, target, f"{target}.px4"),
                os.path.join(DIST_DIR, f"{target}.{PX4_VERSION}.{git_hash}.px4"),
            )


def host(build_pymavlink: bool, build_px4: bool) -> None:
    # code that runs on the host operating system

    # make the target directory
    os.makedirs(DIST_DIR, exist_ok=True)

    subprocess.check_output(
        [
            "git",
            "config",
            "--global",
            "--add",
            "safe.directory",
            os.path.abspath(os.path.join(THIS_DIR, "..")),
        ]
    )
    git_hash = (
        subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=THIS_DIR)
        .decode("utf-8")
        .strip()
    )
    script_cmd = (
        ["python3", "build.py"]
        + sys.argv[1:]
        + ["--container", f"--git-hash={git_hash}"]
    )

    docker_image = "docker.io/px4io/px4-dev-nuttx-focal:latest"
    if build_pymavlink and not build_px4:
        # if only building pymavlink, use a simpler ARM compatible image
        docker_image = "docker.io/library/python:3.9-buster"

    cmd = [
        "docker",
        "run",
        "--rm",
        "-w",
        "/work",
        "-v",
        f"{THIS_DIR}:/work:rw",
        docker_image,
    ] + script_cmd

    print2(f"Running: {' '.join(cmd)}")
    subprocess.check_call(cmd, stdout=sys.stdout, stderr=sys.stderr)

    if build_pymavlink:
        fcm_dir = os.path.join(THIS_DIR, "..", "VMC", "fcm")

        # remove old files
        clean_directory(fcm_dir, [".whl", ".tar.gz"])

        # copy new files
        for filename in os.listdir(DIST_DIR):
            if filename.endswith(".whl") or filename.endswith(".tar.gz"):
                shutil.copyfile(
                    os.path.join(DIST_DIR, filename), os.path.join(fcm_dir, filename)
                )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a PX4/Pymavlink build")
    parser.add_argument("--container", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--git-hash", type=str, help=argparse.SUPPRESS)
    parser.add_argument(
        "--pymavlink", action="store_true", help="Build Pymavlink package"
    )
    parser.add_argument("--px4", action="store_true", help="Build PX4 firmware")

    args = parser.parse_args()

    if args.px4 and platform.machine() == "aarch64":
        parser.error("Sorry, cannot build PX4 on ARM")

    if args.container:
        container(args.pymavlink, args.px4, args.git_hash)
    else:
        host(args.pymavlink, args.px4)
