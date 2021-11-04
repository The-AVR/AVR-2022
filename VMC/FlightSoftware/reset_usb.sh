#!/bin/bash

# https://askubuntu.com/a/15856
# script will NOT work without being run as sudo
if [[ $EUID -ne 0 ]]; then
    echo "This script must be run with 'sudo'"
    exit 1
fi

lsusbbefore="$(lsusb | wc -l)"

# https://askubuntu.com/a/61165
shopt -s globstar

# this resets all of the root usb controllers. should be sufficient
# to reset their child devices as well
for f in /sys/bus/usb/devices/usb*; do
    echo "Disabling $f"
    echo 0 >"$f"/authorized
    sleep 0.2

    echo "Enabling $f"
    echo 1 >"$f"/authorized
    sleep 0.2
done

# Add a sleep after finishing resetting everything
# This is a pretty violent process, so need a second for the USB
# devices to re-register
echo "Finishing..."
sleep 5

# Device IDs will likely change after reset, so just count the number of entries
lsusbafter="$(lsusb | wc -l)"

if [[ "$lsusbbefore" != "$lsusbafter" ]]; then
    echo "'lsusb' command output NOT the same!"
    echo "Something has gone wrong, please restart your Jetson."
    exit 1
fi
