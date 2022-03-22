import argparse
import multiprocessing
import os
import shutil
import subprocess
import sys

# warning, v1.10.2 does not appear to build anymore
PX4_VERSION = "v1.12.3"

THIS_DIR = os.path.abspath(os.path.dirname(__file__))


def print2(msg):
    print(f"--- {msg}", flush=True)


def container(build_pymavlink: bool, build_px4: bool):
    # code that runs inside the container
    px4_dir = os.path.join(THIS_DIR, "build", "PX4-Autopilot")
    pymavlink_dir = os.path.join(THIS_DIR, "build", "pymavlink")

    if os.path.isdir(pymavlink_dir):
        print2("Updating pymavlink")
        subprocess.check_call(["git", "pull"], cwd=pymavlink_dir)
    else:
        print2("Cloning pymavlink")
        subprocess.check_call(
            ["git", "clone", "https://github.com/ardupilot/pymavlink", pymavlink_dir]
        )

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
            os.path.join(pymavlink_dir, "requirements.txt"),
        ]
    )

    if os.path.isdir(px4_dir):
        print2("Resetting PX4 checkout")
        subprocess.check_call(["git", "fetch", "origin"], cwd=px4_dir)
        subprocess.check_call(["git", "checkout", PX4_VERSION], cwd=px4_dir)
        subprocess.check_call(["git", "reset", "--hard", PX4_VERSION], cwd=px4_dir)
        subprocess.check_call(["git", "pull", "--recurse-submodules"], cwd=px4_dir)
    else:
        print2("Cloning PX4")
        subprocess.check_call(
            [
                "git",
                "clone",
                "https://github.com/PX4/PX4-Autopilot",
                px4_dir,
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
        cwd=px4_dir,
    )

    print2("Injecting Bell MAVLink message")
    shutil.copyfile(
        os.path.join(THIS_DIR, "bell.xml"),
        os.path.join(
            px4_dir,
            "mavlink",
            "include",
            "mavlink",
            "v2.0",
            "message_definitions",
            "bell.xml",
        ),
    )
    subprocess.check_call(
        [
            sys.executable,
            "-m",
            "pymavlink.tools.mavgen",
            "--lang=C",
            "--wire-protocol=2.0",
            f"--output={os.path.join(px4_dir, 'mavlink', 'include', 'mavlink', 'v2.0')}",
            os.path.join(
                px4_dir,
                "mavlink",
                "include",
                "mavlink",
                "v2.0",
                "message_definitions",
                "bell.xml",
            ),
        ],
        cwd=os.path.join(pymavlink_dir, ".."),
    )

    # changes need to be committed to build
    # git config does not matter, just need *something* to commit
    subprocess.check_call(
        ["git", "config", "user.email", "github-bot@bellflight.com"], cwd=px4_dir
    )
    subprocess.check_call(["git", "config", "user.name", "Github Actions"], cwd=px4_dir)
    subprocess.check_call(["git", "add", "."], cwd=px4_dir)
    subprocess.check_call(
        ["git", "commit", "-m", "Local commit to facilitate build"], cwd=px4_dir
    )

    if build_pymavlink:
        print2("Generating pymavlink package")

        # copy message definitions from px4 so we're using the exact same version
        shutil.rmtree(
            os.path.join(pymavlink_dir, "message_definitions", "v1.0"),
            ignore_errors=True,
        )
        shutil.copytree(
            os.path.join(
                px4_dir, "mavlink", "include", "mavlink", "v2.0", "message_definitions"
            ),
            os.path.join(pymavlink_dir, "message_definitions", "v1.0"),
        )

        # make a new environment with the mavlink dialect set
        new_env = os.environ.copy()
        new_env["MAVLINK_DIALECT"] = "bell"
        subprocess.check_call(
            [sys.executable, "setup.py", "sdist", "bdist_wheel"],
            cwd=pymavlink_dir,
            env=new_env,
        )

        # copy the outputs to the target directory
        for filename in os.listdir(os.path.join(pymavlink_dir, "dist")):
            shutil.copyfile(
                os.path.join(pymavlink_dir, "dist", filename),
                os.path.join(THIS_DIR, "target", filename),
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
                f"--output={os.path.join(THIS_DIR, 'target', 'bell.lua')}",
                os.path.join(
                    px4_dir,
                    "mavlink",
                    "include",
                    "mavlink",
                    "v2.0",
                    "message_definitions",
                    "bell.xml",
                ),
            ],
            cwd=os.path.join(pymavlink_dir, ".."),
        )

    if build_px4:
        print2("Building PX4 firmware")

        # pixhawk
        subprocess.check_call(
            ["make", "px4_fmu-v5_default", f"-j{multiprocessing.cpu_count()}"],
            cwd=px4_dir,
        )
        shutil.copyfile(
            os.path.join(
                px4_dir, "build", "px4_fmu-v5_default", "px4_fmu-v5_default.px4"
            ),
            os.path.join(THIS_DIR, "target", f"px4_fmu-v5_default.{PX4_VERSION}.px4"),
        )

        # nxp
        subprocess.check_call(
            ["make", "nxp_fmuk66-v3_default", f"-j{multiprocessing.cpu_count()}"],
            cwd=px4_dir,
        )
        shutil.copyfile(
            os.path.join(
                px4_dir, "build", "nxp_fmuk66-v3_default", "nxp_fmuk66-v3_default.px4"
            ),
            os.path.join(
                THIS_DIR, "target", f"nxp_fmuk66-v3_default.{PX4_VERSION}.px4"
            ),
        )


def host(build_pymavlink: bool, build_px4: bool):
    # code that runs on the host operating system

    # make the target directory
    target_dir = os.path.join(THIS_DIR, "target")
    os.makedirs(target_dir, exist_ok=True)

    script_cmd = ["python3", "generate.py", "container"]
    if build_pymavlink:
        script_cmd.append("--pymavlink")
    if build_px4:
        script_cmd.append("--px4")

    cmd = [
        "docker",
        "run",
        "--rm",
        "-w",
        "/work",
        "-v",
        f"{THIS_DIR}:/work:rw",
        "docker.io/px4io/px4-dev-nuttx-focal:latest",
    ] + script_cmd

    print2(f"Running: {' '.join(cmd)}")
    subprocess.check_call(cmd, stdout=sys.stdout, stderr=sys.stderr)

    if build_pymavlink:
        fcm_dir = os.path.join(THIS_DIR, "..", "VMC", "FlightSoftware", "fcm")

        # remove old files
        for filename in os.listdir(fcm_dir):
            if filename.endswith(".whl") or filename.endswith(".tar.gz"):
                os.remove(os.path.join(fcm_dir, filename))

        # copy new files
        for filename in os.listdir(target_dir):
            if filename.endswith(".whl") or filename.endswith(".tar.gz"):
                shutil.copyfile(
                    os.path.join(target_dir, filename), os.path.join(fcm_dir, filename)
                )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a PX4/Pymavlink build")
    parser.add_argument("mode", choices=["host", "container"], help="Launch mode")
    parser.add_argument(
        "--pymavlink", action="store_true", help="Build Pymavlink package"
    )
    parser.add_argument("--px4", action="store_true", help="Build PX4 firmware")

    args = parser.parse_args()

    if args.mode == "host":
        host(args.pymavlink, args.px4)
    elif args.mode == "container":
        container(args.pymavlink, args.px4)
