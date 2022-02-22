#!/bin/bash
set -e

# sometimes when sudo nmcli radio wifi off is run, re-enabling wifi may take
# a hot second. Ideally, should never fully disable wifi, just disconnect, but FYI
sudo nmcli radio wifi on

if [ "$1" == "--connect" ]; then
    echo "Available networks:"
    sudo nmcli device wifi list | head -n 20

    read -r -p "Enter the SSID to connect to: " ssid
    read -r -s -p "Enter the password (leave blank for no password): " password

    # disconnect any existing connections
    sudo nmcli device disconnect wlan0 || true
    # connect
    echo "===== Connecting to network $ssid with password $password ====="
    sudo nmcli device wifi connect "$ssid" password "$password"

elif [ "$1" == "--create" ]; then
    randst=$(echo $RANDOM | md5sum | head -c 10)

    read -r -p "Enter the SSID to create (default 'VRCDrone-$randst'): " ssid
    ssid=${name:-VRCDrone-$randst}
    read -r -p "Enter the password (default 'bellvrc22') (must be at least 8 characters): " password
    password=${name:-bellvrc22}

    # disconnect any existing connections
    sudo nmcli device disconnect wlan0 || true
    # delete old hotspot connection profile
    sudo nmcli connection delete Hotspot || true
    # create hotpsot
    echo "===== Creating network $ssid with password $password ====="
    sudo nmcli device wifi hotspot ifname wlan0 ssid "$ssid" password "$password"

elif [ "$1" == "--disconnect" ]; then
    echo "Disconnecting WiFi, errors are normal"
    sudo nmcli device disconnect wlan0 || true

else
    echo "Usage: wifi.sh [--connect|--create|--disconnect]"
    exit 1
fi