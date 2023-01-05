#!/usr/bin/python3

import argparse
import contextlib
import json
import os
import shutil
import subprocess
from subprocess import Popen, PIPE, CalledProcessError
import sys

# colors
RED = "\033[0;31m"
LIGHTRED = "\033[1;31m"
GREEN = "\033[0;32m"
LIGHTGREEN = "\033[1;32m"
CYAN = "\033[0;36m"
NC = "\033[0m"  # No Color

AVR_DIR = os.path.join(os.path.expanduser("~"), "AVR-2022")

# fmt: off

def check_sudo():
    # skip these checks on Windows
    if sys.platform == "win32":
        return

    if os.geteuid() != 0:
        # re run ourselves with sudo
        print("Needing sudo privileges, re-launching")

        try:
            sys.exit(
                subprocess.run(["sudo", sys.executable, __file__] + sys.argv[1:]).returncode
            )
        except PermissionError:
            sys.exit(0)
        except KeyboardInterrupt:
            sys.exit(1)

def print_bar():
    """
    Print a bar equal to the width of the current terminal.
    """
    print("=" * os.get_terminal_size().columns)


def print_title(title):
    """
    Print a title with a bar.
    """
    print(f"{CYAN}{title}{NC}")
    print_bar()


def original_user_cmd(username, cmd):
    """
    Take a command list, and return a version that runs as the given username.
    """
    return ["sudo", "-u", username, "-i"] + cmd


def main(development, sim):
    if not os.path.isdir(AVR_DIR) and not sim:
        print(f"AVR repository has not been cloned to {AVR_DIR}")
        print(f"Do this with 'git clone --recurse-submodules https://github.com/bellflight/AVR-2022 {AVR_DIR}'")
        sys.exit(1)


    print(f"{RED}")
    print("██████████████████████████████████████████████████████████████████████████")
    print(f"█████████████████████████████████████████████████████████████████████{NC}TM{RED}███")
    print("████▌              ▀████            ████     ██████████     ██████████████")
    print("██████▄▄▄  ▄▄▄▄     ▐███    ▄▄▄▄▄▄▄▄████     ██████████     ██████████████")
    print("███████▀   █████    ████    ▀▀▀▀▀▀▀▀████     ██████████     ██████████████")
    print("███████            ▀████            ████     ██████████     ██████████████")
    print("███████    ▄▄▄▄▄     ███    ████████████     ██████████     ██████████████")
    print("███████    ████▀     ███    ▀▀▀▀▀▀▀▀████     ▀▀▀▀▀▀▀███     ▀▀▀▀▀▀▀▀██████")
    print("███████             ▄███            ████            ███             ██████")
    print("███████▄▄▄▄▄▄▄▄▄▄▄██████▄▄▄▄▄▄▄▄▄▄▄▄████▄▄▄▄▄▄▄▄▄▄▄▄███▄▄▄▄▄▄▄▄▄▄▄▄▄██████")
    print("██████████████████████████████████████████████████████████████████████████")
    print("                                                                          ")
    print("██████████████████████████████▄▄          ▄▄██████████████████████████████")
    print("██████████████████████████████████▄    ▄██████████████████████████████████")
    print("████████████████████████████████████  ████████████████████████████████████")
    print("███▀▀▀▀▀██████████████████████████▀    ▀██████████████████████████▀▀▀▀▀███")
    print("████▄▄          ▀▀▀▀█████████████        █████████████▀▀▀▀          ▄▄████")
    print("████████▄▄▄                ▀▀▀▀▀██████████▀▀▀▀▀                ▄▄▄████████")
    print("█████████████▄▄                   ▀████▀                   ▄▄█████████████")
    print("█████████████████▄                  ██                  ▄█████████████████")
    print("██████████████████████████████▀     ██     ▀██████████████████████████████")
    print("███████████████████████▀▀           ██           ▀▀███████████████████████")
    print("████████████████▀▀▀                 ██                 ▀▀▀████████████████")
    print("█████████▀▀                       ▄████▄                       ▀▀█████████")
    print("████▀▀                         ▄███▀  ▀███▄                         ▀▀████")
    print(" ████▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄█████▀      ▀█████▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄████ ")
    print(" ▀███████████████████████████████▄      ▄███████████████████████████████▀ ")
    print("  ▀████████████████████████████████    ████████████████████████████████▀  ")
    print("    ██████████████████████████████▀    ▀██████████████████████████████    ")
    print("     ▀████████████████████████████▄    ▄████████████████████████████▀     ")
    print("       ▀███████████████████████████    ███████████████████████████▀       ")
    print("         ▀█████████████████████████    █████████████████████████▀         ")
    print("           ▀███████████████████████    ███████████████████████▀           ")
    print("             ▀█████████████████████    █████████████████████▀             ")
    print("               ▀███████████████████    ███████████████████▀               ")
    print("                 ▀█████████████████    █████████████████▀                 ")
    print("                    ▀██████████████    ██████████████▀                    ")
    print("                      ▀████████████    ████████████▀                      ")
    print("                        ▀██████████    ██████████▀                        ")
    print("                           ▀███████    ███████▀                           ")
    print("                             ▀▀████    ████▀▀                             ")
    print("                                ▀███  ███▀                                ")
    print("                                  ▀█▄▄█▀                                  ")
    print(f"{NC}")
    print_bar()

    print_title("Checking git Status")
    orig_username = subprocess.check_output(["id", "-nu", os.environ["SUDO_UID"]]).decode("utf-8").strip()
    # run a few commands as the original user, so as not to break permissons
    print("Configuring credential cache")
    subprocess.check_call(original_user_cmd(orig_username, ["git", "config", "--global", "credential.helper", "cache"]))
    print("Fetching latest code")
    subprocess.check_call(original_user_cmd(orig_username, ["git", f"--git-dir={os.path.join(AVR_DIR, '.git')}", f"--work-tree={AVR_DIR}", "fetch"]), cwd=AVR_DIR)

    # ignore git errors, they're usually due to a missing HEAD file
    # because of weird situations
    with contextlib.suppress(subprocess.CalledProcessError):
        # check if we're on the main branch
        if not development and not sim:
            print("Making sure we're on the main branch")
            current_branch = subprocess.check_output(original_user_cmd(orig_username, ["git", "rev-parse", "--abbrev-ref", "HEAD"]), cwd=AVR_DIR).decode("utf-8").strip()
            if current_branch != "main":
                print(f"{LIGHTRED}WARNING:{NC} Not currently on the main branch, run 'git checkout main && git pull' then re-run this script")
                sys.exit(1)

        # check if we're on the latest commit
        print("Making sure we have the latest code")
        local_commit = subprocess.check_output(original_user_cmd(orig_username, ["git", "rev-parse", "HEAD"]), cwd=AVR_DIR).decode("utf-8").strip()
        upstream_commit = subprocess.check_output(original_user_cmd(orig_username, ["git", "rev-parse", "@{u}"]), cwd=AVR_DIR).decode("utf-8").strip()

        if local_commit != upstream_commit:
            print(f"{LIGHTRED}WARNING:{NC} Remote changes exist that are not present locally. Run 'git pull' then re-run this script")
            sys.exit(1)

    print("Making sure submodules are up-to-date")
    # https://stackoverflow.com/a/64621032
    subprocess.check_call(original_user_cmd(orig_username, ["git", f"--git-dir={os.path.join(AVR_DIR, '.git')}", "--work-tree=.", "-C", AVR_DIR, "submodule", "update", "--init", "--recursive"]), cwd=AVR_DIR)
    print_bar()


    print_title("Updating Package Index")
    subprocess.check_call(["apt-get", "update"])
    print_bar()



    print_title("Upgrading System Packages")
    non_interactive_env = os.environ.copy()
    non_interactive_env["DEBIAN_FRONTEND"] = "noninteractive"
    subprocess.check_call(["apt-get", "upgrade", "-y"], env=non_interactive_env)
    print_bar()



    print_title("Installing Prerequisites")
    # a lot of these are already installed by default
    # but better to be explicit
    packages = [
        "git",
        "ca-certificates",
        "apt-utils",
        "software-properties-common",
        "wget",
        "htop",
        "nano",
        "python3",
        "python3-wheel",
        "python3-pip",
        "unzip"
    ]
    print("Installing apt Packages")
    subprocess.check_call(["apt-get", "install", "-y"] + packages)

    # install pip packages
    print("Installing Python Packages")
    subprocess.check_call(["python3", "-m", "pip", "install", "--upgrade", "pip", "wheel"], stderr=subprocess.DEVNULL)
    subprocess.check_call(["python3", "-m", "pip", "install", "-r", os.path.join(AVR_DIR, "VMC", "scripts", "requirements.txt")], stderr=subprocess.DEVNULL)

    if development:
        subprocess.check_call(["python3", "-m", "pip", "install", "--upgrade", "jetson-stats"], stderr=subprocess.DEVNULL)
    print_bar()


    if not sim:
        print_title("Configuring Jetson Settings")
        # set to high-power 10W mode. 1 is 5W mode
        print("Setting power mode")
        subprocess.check_call(["nvpmodel", "-m", "0"])

        # make sure SPI is enabled
        # header 1 is the 40pin header
        # gotten from `sudo /opt/nvidia/jetson-io/config-by-pin.py -l`
        # https://docs.nvidia.com/jetson/archives/r34.1/DeveloperGuide/text/HR/ConfiguringTheJetsonExpansionHeaders.html#config-by-function-configure-header-s-by-special-function
        print("Enabling SPI")
        subprocess.check_call(["python3", "/opt/nvidia/jetson-io/config-by-function.py", "-o", "dtb", '1=spi1'])
        print_bar()



    print_title("Removing Old Docker Data")
    print("Removing old Docker containers")
    containers = subprocess.check_output(["docker", "container", "ps", "-a", "-q"]).decode("utf-8").splitlines()
    for container in containers:
        subprocess.check_call(["docker", "container", "rm", "-f", container])

    print("Removing old Docker volumes")
    volumes = subprocess.check_output(["docker", "volume", "ls", "-q"]).decode("utf-8").splitlines()
    for volume in volumes:
        subprocess.check_call(["docker", "volume", "rm", volume])
    print_bar()



    print_title("Installing Docker Compose")
    subprocess.check_call(["python3", "-m", "pip", "install", "--upgrade", "docker-compose"], stderr=subprocess.DEVNULL)
    print_bar()


    if not sim:
        print_title("Configuring the Nvidia Docker Runtime")
        # set the nvidia runtime to be default
        # https://lukeyeager.github.io/2018/01/22/setting-the-default-docker-runtime-to-nvidia.html
        daemon_json = "/etc/docker/daemon.json"
        with open(daemon_json, "r") as fp:
            daemon_data = json.load(fp)

        if daemon_data.get("default-runtime", "") != "nvidia":
            print(f"Updating {daemon_json}")

            daemon_data["default-runtime"] = "nvidia"
            assert "nvidia" in daemon_data["runtimes"]

            with open(daemon_json, "w") as fp:
                json.dump(daemon_data, fp, indent=2)

        # needed so that the shared libs are included in the docker container creation from the host
        print("Copying Docker runtime libraries definition")
        shutil.copy(os.path.join(AVR_DIR, "VMC/apriltag/linux/avr.csv"), "/etc/nvidia-container-runtime/host-files-for-container.d/")

        # restart docker so new runtime takes into effect
        print("Restarting Docker service")
        subprocess.check_call(["service", "docker", "stop"])
        subprocess.check_call(["service", "docker", "start"])
        print_bar()



        print_title("Installing Boot Services")
        services = ["spio-mount.service", "fan-100.service"]
        for service in services:
            print(f"Installing {service}")
            shutil.copy(os.path.join(AVR_DIR, "VMC", "scripts", service), "/etc/systemd/system/")
            subprocess.check_call(["systemctl", "enable", service])
            subprocess.check_call(["systemctl", "start", service])
        print_bar()



        print_title("Obtaining ZED Camera Configuration")
        zed_settings_dir = os.path.join(AVR_DIR, 'VMC/vio/settings')

        zed_serial = subprocess.check_output(["docker", "run", "--rm", "--mount", f"type=bind,source={zed_settings_dir},target=/usr/local/zed/settings/", "--privileged", "docker.io/stereolabs/zed:3.7-py-runtime-l4t-r32.6", "python3", "-c", "import pyzed.sl;z=pyzed.sl.Camera();z.open();print(z.get_camera_information().serial_number);z.close();"]).decode("utf-8").strip()
        if zed_serial == "0":
            print(f"{LIGHTRED}WARNING:{NC} ZED camera not detected, skipping settings download")
        else:
            print("ZED camera settings have been downloaded")
        print_bar()

    # make sure at least one settings file exists
    if not development and not sim and not any(f.endswith(".conf") for f in os.listdir(zed_settings_dir)):
        print(f"{RED}EROOR:{NC} ZED settings not found. Your drone will NOT fly. Plug in the ZED camera and try again.")
        sys.exit(1)


    print_title("Building AVR Software")
    # build pymavlink
    if development:
        subprocess.check_call(["python3", os.path.join(AVR_DIR, "PX4", "build.py"), "--pymavlink"])

    # make sure docker is logged in
    proc = subprocess.run(["docker", "pull", "ghcr.io/bellflight/avr/2022/mqtt:latest"])
    if proc.returncode != 0:
        print("Please log into GitHub container registry:")
        subprocess.check_call(["docker", "login", "ghcr.io"])

    # pull images
    cmd = ["python3", os.path.join(AVR_DIR, "VMC", "start.py"), "pull"]
    if sim:
        cmd.append("--sim")
    else:
        cmd.append("--norm")

    if development or sim:
        cmd.append("--local")
    subprocess.check_call(cmd)

    # build images
    cmd = ["python3", os.path.join(AVR_DIR, "VMC", "start.py"), "build"]

    if sim:
        cmd.append("--sim")
    else:
        cmd.append("--norm")

    if development or sim:
        cmd.append("--local")

    with Popen(cmd, stdout=PIPE, bufsize=1, universal_newlines=True) as p:
        for line in p.stdout:
            print(line, end='') # process line here

    if p.returncode != 0:
        raise CalledProcessError(p.returncode, p.args)
    # subprocess.check_call(cmd)
    print_bar()
    # down load simulation world model
    if sim:
        print_title("download simulation world")
        SIM_DIR = os.path.join(AVR_DIR, "sim")
        if not os.path.exists(SIM_DIR):
            os.makedirs(SIM_DIR)

        id = "1SZiwiudzSRgIg5EuPFilLBpKaIFklGcq"
        subprocess.check_call(["gdown", id], cwd=SIM_DIR)
        subprocess.check_call(["unzip", os.path.join(SIM_DIR, "build*.zip")], cwd=SIM_DIR)
        print_bar()
    

    print_title("Cleaning Up")
    subprocess.check_call(["apt-get", "autoremove", "-y"])
    subprocess.check_call(["docker", "system", "prune", "-f"])
    print_bar()


    if not sim:
        print_title("Performing Self-Test")
        print("Testing Nvidia container runtime:")
        proc = subprocess.run(["docker", "run", "--rm", "--gpus", "all", "--env", "NVIDIA_DISABLE_REQUIRE=1", "nvcr.io/nvidia/cuda:11.4.1-base-ubuntu18.04", "echo", "-e", f"{LIGHTGREEN}Passed!{NC}"])
        if proc.returncode != 0:
            print(f"{LIGHTRED}FAILED{NC}")
        print_bar()



    print(f"{GREEN}AVR setup has completed{NC}")
    print(f"{GREEN}Please reboot your VMC{NC}")

   
    if not sim:
        if input("Would you like to reboot now? (y/n): ").lower() == "y":
            subprocess.run(["reboot"])

if __name__ == "__main__":
    check_sudo()

    parser = argparse.ArgumentParser(description="Setup the Jetson for AVR")
    parser.add_argument("--development", "--dev", action="store_true", help="Jetson Development setup")
    parser.add_argument("--sim", action="store_true", help="Desktop Development setup")
    parser.add_argument("--avr-dir")

    args = parser.parse_args()
    if args.avr_dir:
        AVR_DIR = args.avr_dir
    main(args.development, args.sim)
