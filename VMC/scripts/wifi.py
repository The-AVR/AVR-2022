#!/usr/bin/python3

import argparse
import getpass
import os
import subprocess
import sys

# fmt: off

def check_sudo():
    # skip these checks on Windows
    if sys.platform == "win32":
        return

    if os.geteuid() != 0:
        # re run ourselves with sudo
        print("Needing sudo privledges, re-lauching")

        try:
            sys.exit(
                subprocess.run(["sudo", sys.executable, __file__] + sys.argv[1:]).returncode
            )
        except PermissionError:
            sys.exit(0)
        except KeyboardInterrupt:
            sys.exit(1)

def disconnect():
    """
    Disconnect the wlan0 interface
    """
    # supress STDERR here
    subprocess.call(["nmcli", "device", "disconnect", "wlan0"], stderr=subprocess.DEVNULL)

def connect():
    """
    Connect the wlan0 interface
    """
    # print the list of available networks, limited to 20 lines
    output = subprocess.check_output(["nmcli", "device", "wifi", "list"]).decode("utf-8")
    for i, line in enumerate(output.splitlines()):
        if i < 20:
            print(line)

    # get inputs
    ssid = input("Enter the SSID to connect to: ")
    password = getpass.getpass("Enter the password (leave blank for no password): ")

    # disconnect any existing connections
    disconnect()

    # connect
    cmd = ["nmcli", "device", "wifi", "connect", ssid]
    if password:
        cmd.extend(["password", password])

    print(f"===== Connecting to network {ssid} =====")
    subprocess.check_call(cmd)

def create():
    """
    Create a network with the wlan0 interface
    """
    # get the wireless interface's MAC address
    with open("/sys/class/net/wlan0/address", "r") as fp:
        mac_addr = fp.read().strip().replace(":", "")

    default_ssid = f"AVRDrone-{mac_addr}"
    default_password = "bellavr22"

    # get inputs
    ssid = input(f"Enter the SSID to create (default '{default_ssid}'): ")
    if not ssid:
        ssid = default_ssid

    password = input(f"Enter the password (default '{default_password}') (must be at least 8 characters): ")
    if not password:
        password = default_password

    assert len(password) >= 8

    print("===== Removing old connections =====")
    # disconnect any existing connections
    disconnect()

    # delete old hotspot connection profile
    subprocess.call(["nmcli", "connection", "delete", "Hotspot"], stderr=subprocess.DEVNULL)

    # create
    print(f"===== Creating network {ssid} with password {password} =====")
    subprocess.check_call(["nmcli", "device", "wifi", "hotspot", "ifname", "wlan0", "ssid", ssid, "password", password])
    subprocess.check_call(["nmcli", "con", "modify", "Hotspot", "connection.autoconnect", "yes"])

def status():
    """
    Show the currently connected wifi network
    """
    subprocess.check_call(["nmcli", "connection", "show", "--active"])

if __name__ == "__main__":
    check_sudo()

    parser = argparse.ArgumentParser(description="WiFi Setup Script")
    parser.add_argument("action", choices=["connect", "create", "disconnect", "status"])

    args = parser.parse_args()

    if args.action == "connect":
        connect()
    elif args.action == "create":
        create()
    elif args.action == "disconnect":
        disconnect()
    elif args.action == "status":
        status()