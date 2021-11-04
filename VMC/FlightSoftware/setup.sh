#!/bin/bash

# exit when any command fails
set -e

bar () {
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

VRC_DIR=~/VRC

# see if sudo is installed
# mainly for testing with Docker, that doesn't have sudo
s=""
if [ -n "$(which sudo)" ]; then
    s="sudo"
fi

# check to make sure code has already been cloned
if [[ ! -d  $VRC_DIR ]]; then
    echo "VRC repository has not been cloned to $VRC_DIR"
    echo "Do this with '$s apt update && $s apt install -y git && git clone https://github.com/bellflight/VRC-2022 $VRC_DIR'"
    exit 1
fi

echo -e "${RED}"
echo "██████████████████████████████████████████████████████████████████████████"
echo -e "█████████████████████████████████████████████████████████████████████${NC}TM${RED}███"
echo "███████▌              ▀████            ████     ██████████     ███████████"
echo "█████████▄▄▄  ▄▄▄▄     ▐███    ▄▄▄▄▄▄▄▄████     ██████████     ███████████"
echo "██████████▀   █████    ████    ▀▀▀▀▀▀▀▀████     ██████████     ███████████"
echo "██████████            ▀████            ████     ██████████     ███████████"
echo "██████████    ▄▄▄▄▄     ███    ████████████     ██████████     ███████████"
echo "██████████    ████▀     ███    ▀▀▀▀▀▀▀▀████     ▀▀▀▀▀▀▀███     ▀▀▀▀▀▀▀▀███"
echo "██████████             ▄███            ████            ███             ███"
echo "██████████▄▄▄▄▄▄▄▄▄▄▄██████▄▄▄▄▄▄▄▄▄▄▄▄████▄▄▄▄▄▄▄▄▄▄▄▄███▄▄▄▄▄▄▄▄▄▄▄▄▄███"
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
$s apt install -y git apt-transport-https ca-certificates apt-utils software-properties-common gnupg lsb-release unzip curl rsync htop nano python3 python3-wheel python3-pip jq
$s -H python3 -m pip install pip wheel --upgrade
$s -H python3 -m pip install -U jetson-stats --upgrade
# set to high-power 10W mode. 1 is 5W mode
$s nvpmodel -m 0

cd $VRC_DIR
# cache the git credentials (mainly during development)
git config --global credential.helper cache
# update repo
git pull
# switch to main branch
git checkout main
bar


echo -e "${CYAN}Installing and configuring librealsense${NC}"
bar

# this is (possibly) needed to setup the udev rules on the host
$s apt-key adv --keyserver keys.gnupg.net --recv-key F6E65AC044F831AC80A06380C8B3A55A6F3EFCDE || sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-key F6E65AC044F831AC80A06380C8B3A55A6F3EFCDE
$s add-apt-repository "deb https://librealsense.intel.com/Debian/apt-repo bionic main" -u
$s apt install -y librealsense2-udev-rules librealsense2-utils librealsense2-dev

bar


echo -e "${CYAN}Installing and configuring Docker${NC}"
bar

# # replacing the installed system Docker with the latest version breaks stuff
# # remove old docker installation
# $s apt remove -y docker || true
# $s apt remove -y docker-engine|| true
# $s apt remove -y docker.io || true
# $s apt remove -y containerd || true
# $s apt remove -y runc || true

# # add docker GPG key
# curl -fsSL https://download.docker.com/linux/ubuntu/gpg | $s gpg --batch --yes --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
# # add docker repository
# echo \
#   "deb [arch=arm64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
#   $(lsb_release -cs) stable" | $s tee /etc/apt/sources.list.d/docker.list > /dev/null

# # install docker
# $s apt update
# $s apt install -y docker-ce:arm64 docker-ce-cli:arm64 containerd.io:arm64 docker-compose:arm64

# # install nvidia-docker
# distribution=$(. /etc/os-release;echo $ID$VERSION_ID) \
#    && curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | $s apt-key add - \
#    && curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | $s tee /etc/apt/sources.list.d/nvidia-docker.list
# $s apt update
# $s apt install -y --allow-downgrades \
#        jq \
#        nvidia-docker2:arm64=2.5.0-1 \
#        libnvidia-container-tools:arm64=1.3.3-1 \
#        nvidia-container-runtime:arm64=3.4.2-1 \
#        libnvidia-container1:arm64=1.3.3-1 \
#        nvidia-container-toolkit:arm64=1.4.2-1

# upgrade compose
$s -H python3 -m pip install docker-compose --upgrade

# set the nvidia runtime to be default
# https://lukeyeager.github.io/2018/01/22/setting-the-default-docker-runtime-to-nvidia.html
pushd "$(mktemp -d)"
($s cat /etc/docker/daemon.json 2>/dev/null || echo '{}') | jq '. + {"default-runtime": "nvidia"}' | tee tmp.json
$s mv tmp.json /etc/docker/daemon.json
popd

# needed so that the shared libs are included in the docker container creation from the host
$s cp VMC/FlightSoftware/apriltag/linux/vrc.csv /etc/nvidia-container-runtime/host-files-for-container.d/

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


echo -e "${CYAN}Preparing VRC software${NC}"
bar
cd $VRC_DIR
$s docker-compose pull
$s docker-compose build
bar


echo -e "${CYAN}Cleaning up${NC}"
bar
$s apt autoremove -y
bar


echo -e "${CYAN}Performing self-test${NC}"
bar

# make sure jtop got installed
echo -n "Making sure 'jtop' works... "
if [ -n "$(which jtop)" ]; then
    echo -e "${LIGHTGREEN}Passed!${NC}"
else
    echo -e "${LIGHTRED}Failed!${NC}"
    exit 1
fi

# make sure rs-enumerate-devices
echo -n "Making sure 'rs-enumerate-devices' works... "
if [ -n "$(which rs-enumerate-devices)" ]; then
    echo -e "${LIGHTGREEN}Passed!${NC}"
else
    echo -e "${LIGHTRED}Failed!${NC}"
    exit 1
fi

# ensure the container runtime works
echo -n "Testing Nvidia container runtime... "
($s docker run --rm --gpus all --env NVIDIA_DISABLE_REQUIRE=1 nvcr.io/nvidia/cuda:11.4.1-base-ubuntu18.04 echo -e "${LIGHTGREEN}Passed!${NC}") || echo -e "${LIGHTRED}Failed!${NC}"

bar

echo  -e "${GREEN}VRC Phase 2 finished setting up!${NC}"
echo  -e "${GREEN}Please reboot your VMC now.${NC}"
bar
