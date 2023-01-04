FROM ubuntu:20.04
ARG PX4_VER=v1.13.2

# Need Git to checkout our sources
RUN apt-get update && apt-get install -y git

# Download PX4 requirements
# Trick to get apt-get to not prompt for timezone in tzdata
ENV DEBIAN_FRONTEND=noninteractive

# Need sudo and lsb-release for the installation prerequisites
RUN apt-get install -y sudo lsb-release tzdata wget

# Now grab PX4 from GitHub
RUN git clone https://github.com/PX4/Firmware.git

WORKDIR /Firmware

# Checkout the right branch/tag
RUN git checkout ${PX4_VER} 

# RUN git config --global http.sslVerify false

# Pull submodules
RUN git submodule update --init --recursive


WORKDIR /Firmware/Tools/setup
RUN chmod +x ubuntu.sh
RUN ./ubuntu.sh --no-nuttx

WORKDIR /Firmware

#############################
# Enable Plugins

# Gstreamer for video
# RUN sed -i -e 's/option(BUILD_GSTREAMER_PLUGIN "enable gstreamer plugin" OFF)/option(BUILD_GSTREAMER_PLUGIN "enable gstreamer plugin" ON)/g' Tools/sitl_gazebo/CMakeLists.txt
# Fix Old-style APT repos (https://askubuntu.com/questions/549777/getting-404-not-found-errors-when-doing-sudo-apt-get-update)
# RUN sed -i -e 's/:\/\/(archive.ubuntu.com\|security.ubuntu.com)/old-releases.ubuntu.com/g' /etc/apt/sources.list
RUN apt-get update
# Install GStreamer
# RUN apt-get install $(apt-cache --names-only search ^gstreamer1.0-* | awk '{ print $1 }' | grep -v gstreamer1.0-hybris ) -y

# END Enable Plugins
#############################

# Now start build instructions from https://dev.px4.io/en/setup/building_px4.html


RUN apt-get install -y python3-dev python3-opencv python3-wxgtk4.0 python3-pip python3-matplotlib python3-lxml python3-pygame
RUN pip3 install PyYAML mavproxy --user

# UDP 14550 is what the sim exposes by default
#https://dev.px4.io/en/simulation/


# just build; don't run; https://github.com/PX4/Firmware/issues/3961
RUN DONT_RUN=1 make px4_sitl_default none_iris 
# RUN DONT_RUN=1 make px4_sitl_default jmavsim

# Env Variables
ENV PX4_HOME_LAT 42.3898
ENV PX4_HOME_LON -71.1476
ENV PX4_HOME_ALT 14.2
ENV HOST_IP 172.20.1.83


COPY entrypoint.sh /
RUN chmod +x /entrypoint.sh
ENTRYPOINT /entrypoint.sh 

# Entrypoint
# ENTRYPOINT make px4_sitl_default none_iris
# ENTRYPOINT HEADLESS=1 make px4_sitl_default jmavsim