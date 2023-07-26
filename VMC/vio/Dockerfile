# adapted from https://github.com/stereolabs/zed-docker/blob/master/3.X/jetpack_4.X/py-runtime/Dockerfile

FROM nvcr.io/nvidia/l4t-base:r32.6.1

ENV L4T_MINOR_VERSION=6.1
ENV ZED_SDK_MAJOR=3
ENV ZED_SDK_MINOR=6
ENV JETPACK_MAJOR=4
ENV JETPACK_MINOR=6

ENV PYTHON_VERSION=3.10

ENV DEBIAN_FRONTEND noninteractive

# Fix numpy issues
ENV OPENBLAS_CORETYPE AARCH64

# Install Python newer than 3.6
RUN apt-get update -y || true \
 && apt-get install -y ca-certificates software-properties-common && update-ca-certificates
RUN add-apt-repository ppa:deadsnakes/ppa \
 && apt-get update -y

# Install Python 3.10
# https://github.com/deadsnakes/issues/issues/251
WORKDIR /work/
RUN apt-get update -y
RUN apt-get install -y tzdata curl ca-certificates
RUN curl -L -O https://github.com/bellflight/AVR-Python-arm-deb/releases/download/release/libpython3.10-minimal_3.10.11-1+bionic1_arm64.deb \
 && curl -L -O https://github.com/bellflight/AVR-Python-arm-deb/releases/download/release/libpython3.10-stdlib_3.10.11-1+bionic1_arm64.deb \
 && curl -L -O https://github.com/bellflight/AVR-Python-arm-deb/releases/download/release/python3.10-distutils_3.10.11-1+bionic1_all.deb \
 && curl -L -O https://github.com/bellflight/AVR-Python-arm-deb/releases/download/release/python3.10-lib2to3_3.10.11-1+bionic1_all.deb \
 && curl -L -O https://github.com/bellflight/AVR-Python-arm-deb/releases/download/release/python3.10-minimal_3.10.11-1+bionic1_arm64.deb \
 && curl -L -O https://github.com/bellflight/AVR-Python-arm-deb/releases/download/release/python3.10_3.10.11-1+bionic1_arm64.deb
RUN dpkg -i libpython3.10-minimal_3.10.11-1+bionic1_arm64.deb \
 && dpkg -i libpython3.10-stdlib_3.10.11-1+bionic1_arm64.deb \
 && dpkg -i python3.10-lib2to3_3.10.11-1+bionic1_all.deb \
 && dpkg -i python3.10-distutils_3.10.11-1+bionic1_all.deb \
 && dpkg -i python3.10-minimal_3.10.11-1+bionic1_arm64.deb \
 && dpkg -i python3.10_3.10.11-1+bionic1_arm64.deb \
 && rm *.deb
RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python${PYTHON_VERSION} \
 && python${PYTHON_VERSION} -m pip install pip wheel setuptools --upgrade

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

RUN python3.10 -m pip install -r requirements.txt

COPY . .

CMD ["python3.10", "vio.py"]
