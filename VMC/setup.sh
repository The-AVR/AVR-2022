#!/bin/bash

# flag to turn off some steps during development
if [ "$1" == "--dev" ]; then
    DEVELOPMENT=true
else
    DEVELOPMENT=false
fi

# exit when any command fails
set -e

bar() {
    # prints a bar equal to the current terminal width
    printf '=%.0s' $(seq 1 "$(tput cols)") && printf "\n"
}

# colors
RED='\033[0;31m'
LIGHTRED='\033[1;31m'
GREEN='\033[0;32m'
LIGHTGREEN='\033[1;32m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

VRC_DIR=~/VRC-2022

# see if sudo is installed
# mainly for DEVELOPMENT with Docker, that doesn't have sudo
s=""
if [ -n "$(which sudo)" ]; then
    s="sudo"
fi

# check to make sure code has already been cloned
if [[ ! -d $VRC_DIR ]]; then
    echo "VRC repository has not been cloned to $VRC_DIR"
    echo "Do this with '$s apt update && $s apt install -y git && git clone --recurse-submodules https://github.com/bellflight/VRC-2022 $VRC_DIR'"
    exit 1
fi

echo -e "${RED}"
echo "██████████████████████████████████████████████████████████████████████████"
echo -e "█████████████████████████████████████████████████████████████████████${NC}TM${RED}███"
echo "████▌              ▀████            ████     ██████████     ██████████████"
echo "██████▄▄▄  ▄▄▄▄     ▐███    ▄▄▄▄▄▄▄▄████     ██████████     ██████████████"
echo "███████▀   █████    ████    ▀▀▀▀▀▀▀▀████     ██████████     ██████████████"
echo "███████            ▀████            ████     ██████████     ██████████████"
echo "███████    ▄▄▄▄▄     ███    ████████████     ██████████     ██████████████"
echo "███████    ████▀     ███    ▀▀▀▀▀▀▀▀████     ▀▀▀▀▀▀▀███     ▀▀▀▀▀▀▀▀██████"
echo "███████             ▄███            ████            ███             ██████"
echo "███████▄▄▄▄▄▄▄▄▄▄▄██████▄▄▄▄▄▄▄▄▄▄▄▄████▄▄▄▄▄▄▄▄▄▄▄▄███▄▄▄▄▄▄▄▄▄▄▄▄▄██████"
echo "██████████████████████████████████████████████████████████████████████████"
echo "                                                                          "
echo "██████████████████████████████▄▄          ▄▄██████████████████████████████"
echo "██████████████████████████████████▄    ▄██████████████████████████████████"
echo "████████████████████████████████████  ████████████████████████████████████"
echo "███▀▀▀▀▀██████████████████████████▀    ▀██████████████████████████▀▀▀▀▀███"
echo "████▄▄          ▀▀▀▀█████████████        █████████████▀▀▀▀          ▄▄████"
echo "████████▄▄▄                ▀▀▀▀▀██████████▀▀▀▀▀                ▄▄▄████████"
echo "█████████████▄▄                   ▀████▀                   ▄▄█████████████"
echo "█████████████████▄                  ██                  ▄█████████████████"
echo "██████████████████████████████▀     ██     ▀██████████████████████████████"
echo "███████████████████████▀▀           ██           ▀▀███████████████████████"
echo "████████████████▀▀▀                 ██                 ▀▀▀████████████████"
echo "█████████▀▀                       ▄████▄                       ▀▀█████████"
echo "████▀▀                         ▄███▀  ▀███▄                         ▀▀████"
echo " ████▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄█████▀      ▀█████▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄████ "
echo " ▀███████████████████████████████▄      ▄███████████████████████████████▀ "
echo "  ▀████████████████████████████████    ████████████████████████████████▀  "
echo "    ██████████████████████████████▀    ▀██████████████████████████████    "
echo "     ▀████████████████████████████▄    ▄████████████████████████████▀     "
echo "       ▀███████████████████████████    ███████████████████████████▀       "
echo "         ▀█████████████████████████    █████████████████████████▀         "
echo "           ▀███████████████████████    ███████████████████████▀           "
echo "             ▀█████████████████████    █████████████████████▀             "
echo "               ▀███████████████████    ███████████████████▀               "
echo "                 ▀█████████████████    █████████████████▀                 "
echo "                    ▀██████████████    ██████████████▀                    "
echo "                      ▀████████████    ████████████▀                      "
echo "                        ▀██████████    ██████████▀                        "
echo "                           ▀███████    ███████▀                           "
echo "                             ▀▀████    ████▀▀                             "
echo "                                ▀███  ███▀                                "
echo "                                  ▀█▄▄█▀                                  "
echo -e "${NC}"
bar

echo -e "${CYAN}Updating package index${NC}"
bar
$s apt update
bar

echo -e "${CYAN}Updating system packages${NC}"
bar
export DEBIAN_FRONTEND=noninteractive
# upgrade existing packages
$s DEBIAN_FRONTEND=noninteractive apt upgrade -y
bar

echo -e "${CYAN}Installing prerequisites${NC}"
bar
# install some useful prereqs
$s apt install -y git apt-transport-https ca-certificates apt-utils software-properties-common wget htop nano python3 python3-wheel python3-pip jq python-is-python3
$s -H python3 -m pip install pip wheel --upgrade
$s -H python3 -m pip install -r $VRC_DIR/VMC/scripts/requirements.txt
# set to high-power 10W mode. 1 is 5W mode
$s nvpmodel -m 0

cd $VRC_DIR
# cache the git credentials (mainly during development)
git config --global credential.helper cache
# update repo
git pull
git submodule update --init --recursive
# switch to main branch
if [ "$DEVELOPMENT" != true ] ; then
    git checkout main
fi
bar

echo -e "${CYAN}Installing and configuring Docker${NC}"
bar

# downgrade docker to specific version
# this got pulled from apt sources for some reason
# replacing the installed system Docker with the latest version breaks stuff, so leave as legacy docker.io package
# wget http://launchpadlibrarian.net/561342197/docker.io_20.10.7-0ubuntu1~18.04.2_arm64.deb
# $s DEBIAN_FRONTEND=noninteractive apt install -y --allow-downgrades ./docker.io_20.10.7-0ubuntu1~18.04.2_arm64.deb
# rm docker.io_20.10.7-0ubuntu1~18.04.2_arm64.deb

# upgrade compose
$s -H python3 -m pip install docker-compose --upgrade

# set the nvidia runtime to be default
# https://lukeyeager.github.io/2018/01/22/setting-the-default-docker-runtime-to-nvidia.html
pushd "$(mktemp -d)"
($s cat /etc/docker/daemon.json 2>/dev/null || echo '{}') | jq '. + {"default-runtime": "nvidia"}' | tee tmp.json
$s mv tmp.json /etc/docker/daemon.json
popd

# needed so that the shared libs are included in the docker container creation from the host
$s cp $VRC_DIR/VMC/apriltag/linux/vrc.csv /etc/nvidia-container-runtime/host-files-for-container.d/

# restart docker so new runtime takes into effect
$s service docker stop
$s service docker start

# set up group rights for docker
# had issues with the script suddenly exiting, commented out
# set +e
# $s groupadd docker
# $s usermod -aG docker "$USER"
# newgrp docker
# set -e
bar

echo -e "${CYAN}Installing spio service${NC}"
bar
$s cp $VRC_DIR/VMC/scripts/spio-mount.service /etc/systemd/system/spio-mount.service
$s systemctl enable spio-mount.service
$s systemctl start spio-mount.service
bar

echo -e "${CYAN}Preparing VRC software${NC}"
bar
if [ "$DEVELOPMENT" != true ] ; then
    cd $VRC_DIR
    $s python3 PX4/generate.py --pymavlink
    python3 scripts/copy_libraries.py

    cd $VRC_DIR/VMC
    $s python3 start.py pull --norm
    $s python3 start.py build --norm
else
    cd $VRC_DIR/VMC
    $s python3 start.py pull --norm --local
    $s python3 start.py build --norm --local
fi
bar

echo -e "${CYAN}Obtaining ZED camera configuration${NC}"
bar
zedserial=$($s docker run --rm --mount type=bind,source=$VRC_DIR/VMC/vio/settings,target=/usr/local/zed/settings/ --privileged docker.io/stereolabs/zed:3.7-py-runtime-l4t-r32.6 python3 -c "import pyzed.sl;z=pyzed.sl.Camera();z.open();print(z.get_camera_information().serial_number);z.close();")
if [ "$zedserial" == "0" ] ; then
    echo -e "${LIGHTRED}WARNING:${NC} ZED camera not detected, skipping settings download"
else
    echo "ZED camera settings have been downloaded"
fi
bar

echo -e "${CYAN}Cleaning up${NC}"
bar
$s apt autoremove -y
bar

echo -e "${CYAN}Performing self-test${NC}"
bar
# ensure the container runtime works
# KEEP THIS, saved our bacon once
echo -n "Testing Nvidia container runtime... "
($s docker run --rm --gpus all --env NVIDIA_DISABLE_REQUIRE=1 nvcr.io/nvidia/cuda:11.4.1-base-ubuntu18.04 echo -e "${LIGHTGREEN}Passed!${NC}") || (echo -e "${LIGHTRED}Failed!${NC}" && exit 1)
bar

echo -e "${GREEN}VRC 2022 finished setting up!${NC}"
echo -e "${GREEN}Please reboot your VMC.${NC}"
bar
