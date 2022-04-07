# adapted from https://github.com/stereolabs/zed-docker/blob/master/3.X/jetpack_4.X/py-runtime/Dockerfile

FROM nvcr.io/nvidia/l4t-base:r32.6.1-py3

ENV L4T_MINOR_VERSION=6.1
ENV ZED_SDK_MAJOR=3
ENV ZED_SDK_MINOR=6
ENV JETPACK_MAJOR=4
ENV JETPACK_MINOR=6

ENV DEBIAN_FRONTEND noninteractive

# Install Python newer than 3.6
RUN apt-get update -y || true \
 && apt-get install -y ca-certificates software-properties-common && update-ca-certificates
RUN add-apt-repository ppa:deadsnakes/ppa \
 && apt-get update -y
RUN apt-get install -y \
    python3.9 \
    python3.9-dev \
    python3.9-distutils \
    python3-pip
RUN python3.9 -m pip install pip wheel setuptools --upgrade
# I understand this is bad to do, but the ZEDSDK installs a bunch of
# packages into `python3`, so setting this to our desired version reduces
# duplicate installs
RUN rm /usr/bin/python3 && ln -s /usr/bin/python3.9 /usr/bin/python3

# This environment variable is needed to use the streaming features on Jetson inside a container
ENV LOGNAME root

# This also installs the Python Zed package
RUN apt-get update -y && apt-get install --no-install-recommends lsb-release wget less udev sudo apt-transport-https -y \
 && echo "# R32 (release), REVISION: ${L4T_MINOR_VERSION}" > /etc/nv_tegra_release ; \
 wget -q -O ZED_SDK_Linux_JP.run https://download.stereolabs.com/zedsdk/${ZED_SDK_MAJOR}.${ZED_SDK_MINOR}/jp${JETPACK_MAJOR}${JETPACK_MINOR}/jetsons \
 && chmod +x ZED_SDK_Linux_JP.run ; ./ZED_SDK_Linux_JP.run silent runtime_only \
 && rm -rf /usr/local/zed/resources/* \
 && rm -rf ZED_SDK_Linux_JP.run \
 && apt-get remove --purge build-essential python3.9-dev -y && apt-get autoremove -y \
 && rm -rf /var/lib/apt/lists/*

# This symbolic link is needed to use the streaming features on Jetson inside a container
RUN ln -sf /usr/lib/aarch64-linux-gnu/tegra/libv4l2.so.0 /usr/lib/aarch64-linux-gnu/libv4l2.so

WORKDIR /app

COPY requirements.txt requirements.txt

RUN python3.9 -m pip install -r requirements.txt

COPY . .
COPY ./*.conf /usr/local/zed/settings/

CMD ["python3.9", "vio.py"]
