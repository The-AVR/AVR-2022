FROM ubuntu:20.04
ARG PX4_VER=v1.13.2

# Need Git to checkout our sources
RUN apt-get update && apt-get install -y git

# Download PX4 requirements
# Trick to get apt-get to not prompt for timezone in tzdata
ENV DEBIAN_FRONTEND=noninteractive

# Need sudo and lsb-release for the installation prerequisites
RUN apt-get install -y sudo lsb-release tzdata wget gnupg2

WORKDIR /app

########## INSTALL MAVP2P########
ENV MAVP2P_VERSION=0.7.0
WORKDIR /app

RUN wget --no-check-certificate https://github.com/aler9/mavp2p/releases/download/v${MAVP2P_VERSION}/mavp2p_v${MAVP2P_VERSION}_linux_$(dpkg --print-architecture).tar.gz \
 && tar -xvzf mavp2p*.tar.gz \
 && rm mavp2p*.tar.gz

##################################

# Now grab PX4 from GitHub
RUN git -c http.sslVerify=False clone https://github.com/PX4/PX4-Autopilot.git

WORKDIR /app/PX4-Autopilot

# Checkout the right branch/tag
RUN git -c http.sslVerify=False checkout ${PX4_VER} 

# Pull submodules
RUN git -c http.sslVerify=False submodule update --init --recursive

# Run the PX4 dev tools setup
WORKDIR /app/PX4-Autopilot/Tools/setup
RUN chmod +x ubuntu.sh
RUN ./ubuntu.sh --no-nuttx

WORKDIR /app/PX4-Autopilot

# just build; don't run; https://github.com/PX4/Firmware/issues/3961
RUN HEADLESS=1 DONT_RUN=1 make px4_sitl_default gazebo

# Env Variables
ARG PX4_HOME_LAT=32.803773
ARG PX4_HOME_LON=-97.164095
ARG PX4_HOME_ALT=160

ENV PX4_HOME_LAT=$PX4_HOME_LAT
ENV PX4_HOME_LON=$PX4_HOME_LON
ENV PX4_HOME_ALT=$PX4_HOME_ALT


COPY ./entrypoint.sh ./entrypoint.sh

RUN chmod +x entrypoint.sh

# Entrypoint
ENTRYPOINT ["/bin/bash", "-l", "-c", "./entrypoint.sh"]