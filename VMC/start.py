#!/usr/bin/python3

import argparse
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import warnings
import json
from typing import Any, List

import yaml

IMAGE_BASE = "ghcr.io/bellflight/avr/2022/"
THIS_DIR = os.path.abspath(os.path.dirname(__file__))


def check_sudo() -> None:
    # skip these checks on Windows
    if sys.platform == "win32":
        return

    # Check if Docker requires sudo
    result = subprocess.run(
        ["docker", "info"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    if result.returncode == 0:
        # either we have permission to run docker as non-root
        # or we have sudo
        return

    # re run ourselves with sudo
    print("Needing sudo privileges to run docker, re-launching")

    try:
        sys.exit(
            subprocess.run(["sudo", sys.executable, __file__] + sys.argv[1:]).returncode
        )
    except PermissionError:
        sys.exit(0)
    except KeyboardInterrupt:
        sys.exit(1)


def apriltag_service(compose_services: dict) -> None:
    apriltag_data = {
        "depends_on": ["mqtt"],
        "build": os.path.join(THIS_DIR, "apriltag"),
        "restart": "unless-stopped",
        "volumes": ["/tmp/argus_socket:/tmp/argus_socket"],
    }

    compose_services["apriltag"] = apriltag_data


def fcm_service(compose_services: dict, local: bool = False) -> None:
    fcm_data = {
        "depends_on": ["mqtt", "mavp2p"],
        "restart": "unless-stopped",
    }

    if local:
        fcm_data["build"] = os.path.join(THIS_DIR, "fcm")
    else:
        fcm_data["image"] = f"{IMAGE_BASE}fcm:latest"

    compose_services["fcm"] = fcm_data


def fusion_service(compose_services: dict, local: bool = False) -> None:
    fusion_data = {
        "depends_on": ["mqtt", "vio"],
        "restart": "unless-stopped",
    }

    if local:
        fusion_data["build"] = os.path.join(THIS_DIR, "fusion")
    else:
        fusion_data["image"] = f"{IMAGE_BASE}fusion:latest"

    compose_services["fusion"] = fusion_data


def mavp2p_service(compose_services: dict, local: bool = False, sim: bool = False) -> None:
    if sim:
        mavp2p_data = {
            "restart": "unless-stopped",
            "ports": ["5760:5760/tcp"],
            "command": " udpc:fcm:14541 udpc:fcm:14542",

        }
    else:
        mavp2p_data = {
            "restart": "unless-stopped",
            "devices": ["/dev/ttyTHS1:/dev/ttyTHS1"],
            "ports": ["5760:5760/tcp"],
            "command": "serial:/dev/ttyTHS1:500000 tcps:0.0.0.0:5760 udpc:fcm:14541 udpc:fcm:14542",
        }

    if local:
        if sim:
            mavp2p_data["build"] = {
            "context" :  os.path.join(THIS_DIR, "mavp2p"),
            "args" : {
                        "ARCH" : "amd64",
                        "MAVP2P_ARCH" : "amd64"
                    }
            } 
        else:
            mavp2p_data["build"] = os.path.join(THIS_DIR, "mavp2p")
    else:
        mavp2p_data["image"] = f"{IMAGE_BASE}mavp2p:latest"

    compose_services["mavp2p"] = mavp2p_data


def mqtt_service(compose_services: dict, local: bool = False) -> None:
    mqtt_data = {
        "ports": ["18830:18830"],
        "restart": "unless-stopped",
    }

    if local:
        mqtt_data["build"] = os.path.join(THIS_DIR, "mqtt")
    else:
        mqtt_data["image"] = f"{IMAGE_BASE}mqtt:latest"

    compose_services["mqtt"] = mqtt_data


def pcm_service(compose_services: dict, local: bool = False) -> None:
    pcm_data = {
        "depends_on": ["mqtt"],
        "restart": "unless-stopped",
        "devices": ["/dev/ttyACM0:/dev/ttyACM0"],
    }

    if local:
        pcm_data["build"] = os.path.join(THIS_DIR, "pcm")
    else:
        pcm_data["image"] = f"{IMAGE_BASE}pcm:latest"

    compose_services["pcm"] = pcm_data


def sandbox_service(compose_services: dict) -> None:
    sandbox_data = {
        "depends_on": ["mqtt"],
        "build": os.path.join(THIS_DIR, "sandbox"),
        "restart": "unless-stopped",
    }

    compose_services["sandbox"] = sandbox_data


def status_service(compose_services: dict, local: bool = False) -> None:
    # don't create a volume for nvpmodel if it's not available
    nvpmodel_source = shutil.which("nvpmodel")

    status_data = {
        "depends_on": ["mqtt"],
        "restart": "unless-stopped",
        "privileged": True,
        "volumes": [
            {
                "type": "bind",
                "source": "/etc/nvpmodel.conf",
                "target": "/app/nvpmodel.conf",
            },
        ],
    }

    if nvpmodel_source:
        status_data["volumes"].append(
            {
                "type": "bind",
                "source": nvpmodel_source,
                "target": "/app/nvpmodel",
            }
        )
    else:
        warnings.warn("nvpmodel is not found")

    if local:
        status_data["build"] = os.path.join(THIS_DIR, "status")
    else:
        status_data["image"] = f"{IMAGE_BASE}status:latest"

    compose_services["status"] = status_data


def thermal_service(compose_services: dict, local: bool = False) -> None:
    thermal_data = {
        "depends_on": ["mqtt"],
        "restart": "unless-stopped",
        "privileged": True,
    }

    if local:
        thermal_data["build"] = os.path.join(THIS_DIR, "thermal")
    else:
        thermal_data["image"] = f"{IMAGE_BASE}thermal:latest"

    compose_services["thermal"] = thermal_data


def vio_service(compose_services: dict, local: bool = False) -> None:
    vio_data = {
        "depends_on": ["mqtt"],
        "restart": "unless-stopped",
        "privileged": True,
        "volumes": [
            f"{os.path.join(THIS_DIR, 'vio', 'settings')}:/usr/local/zed/settings/"
        ],
    }

    if local:
        vio_data["build"] = os.path.join(THIS_DIR, "vio")
    else:
        vio_data["image"] = f"{IMAGE_BASE}vio:latest"

    compose_services["vio"] = vio_data

def px4_service(compose_services: dict, local: bool = False) -> None:
    with open(os.path.join(THIS_DIR, "..", "PX4", "version.json"), "r") as fp:
        PX4_VERSION = json.load(fp)

    px4_data = {
        "build" : {
            "context" :  os.path.join(THIS_DIR, "..", "PX4", "docker"),
            "args" : {
                        "PX4_VER" : PX4_VERSION,
                    }
            }
        }   
    compose_services["px4"] = px4_data
             

def prepare_compose_file(local: bool = False, sim: bool = False) -> str:
    # prepare compose services dict
    compose_services = {}

    apriltag_service(compose_services)
    fcm_service(compose_services, local)
    fusion_service(compose_services, local)
    mavp2p_service(compose_services, local, sim)
    mqtt_service(compose_services, local)
    pcm_service(compose_services, local)
    sandbox_service(compose_services)
    thermal_service(compose_services, local)
    vio_service(compose_services, local)
    px4_service(compose_services, local)

    # nvpmodel not available on Windows
    if os.name != "nt":
        status_service(compose_services, local)

    # construct full dict
    compose_data = {"version": "3", "services": compose_services}

    # write compose file
    compose_file = tempfile.mkstemp(prefix="docker-compose-", suffix=".yml")[1]
    print(compose_file)
    with open(compose_file, "w") as fp:
        yaml.dump(compose_data, fp)

    # return file path
    return compose_file


def main(action: str, modules: List[str], local: bool = False, sim: bool = False) -> None:
    compose_file = prepare_compose_file(local, sim)

    # run docker-compose
    project_name = "AVR-2022"
    if os.name == "nt":
        # for some reason on Windows docker-compose doesn't like upper case???
        project_name = project_name.lower()

    cmd = ["docker-compose", "--project-name", project_name, "--file", compose_file]

    if action == "build":
        cmd += ["build"] + modules
    elif action == "pull":
        cmd += ["pull"] + modules
    elif action == "run":
        cmd += ["up", "--remove-orphans", "--force-recreate"] + modules
    elif action == "stop":
        cmd += ["down", "--remove-orphans", "--volumes"]
    else:
        # shouldn't happen
        raise ValueError(f"Unknown action: {action}")

    print(f"Running command: {' '.join(cmd)}")
    proc = subprocess.Popen(cmd, cwd=THIS_DIR)

    def signal_handler(sig: Any, frame: Any) -> None:
        if sys.platform == "win32":
            proc.send_signal(signal.CTRL_BREAK_EVENT)
        else:
            proc.send_signal(signal.SIGINT)

    signal.signal(signal.SIGINT, signal_handler)
    proc.wait()

    # cleanup
    # try:
    #     os.remove(compose_file)
    # except PermissionError:
    #     pass

    sys.exit(proc.returncode)


# sourcery skip: merge-duplicate-blocks, remove-redundant-if
if __name__ == "__main__":
    check_sudo()

    min_modules = ["fcm", "fusion", "mavp2p", "mqtt", "vio"]
    norm_modules = min_modules + ["apriltag", "pcm", "status", "thermal"]
    sim_modules = [ "fcm", "mavp2p", "mqtt", "px4"]
    all_modules = norm_modules + ["sandbox"]


    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-l",
        "--local",
        action="store_true",
        help="Build containers locally rather than using pre-built ones from GitHub",
    )

    parser.add_argument(
        "action", choices=["run", "build", "pull", "stop"], help="Action to perform"
    )
    parser.add_argument(
        "modules",
        nargs="*",
        help="Explicitly list which module(s) to perform the action one",
    )

    exgroup = parser.add_mutually_exclusive_group()
    exgroup.add_argument(
        "-m",
        "--min",
        action="store_true",
        help=f"Perform action on minimal modules ({', '.join(sorted(min_modules))}). Adds to any modules explicitly specified.",
    )
    exgroup.add_argument(
        "-n",
        "--norm",
        action="store_true",
        help=f"Perform action on normal modules ({', '.join(sorted(norm_modules))}). Adds to any modules explicitly specified. If nothing else is specified, this is the default.",
    )
    exgroup.add_argument(
        "-a",
        "--all",
        action="store_true",
        help=f"Perform action on all modules ({', '.join(sorted(all_modules))}). Adds to any modules explicitly specified.",
    )
    exgroup.add_argument(
        "-s",
        "--sim",
        action="store_true",
        help=f"Perform action on simulation modules ({', '.join(sorted(sim_modules))}).",
    )


    args = parser.parse_args()

    if args.min:
        # minimal modules selected
        args.modules += min_modules
    elif args.norm:
        # normal modules selected
        args.modules += norm_modules
    elif args.sim:
        # sim modules selected
        args.modules = sim_modules
    elif args.all:
        # all modules selected
        args.modules += all_modules
    elif not args.modules:
        # nothing specified, default to normal
        args.modules = norm_modules


    args.modules = list(set(args.modules))  # remove duplicates
    main(action=args.action, modules=args.modules, local=args.local, sim=args.sim)
