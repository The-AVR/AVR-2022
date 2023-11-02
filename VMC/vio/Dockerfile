#https://ngc.nvidia.com/catalog/containers/nvidia:l4t-base
FROM nvcr.io/nvidia/l4t-base:r35.1.0

ENV L4T_MAJOR_VERSION=35
ENV L4T_MINOR_VERSION=1
ENV L4T_PATCH_VERSION=0
ENV L4T_BASE_IMAGE=l4t-base
ENV ZED_SDK_MAJOR=3
ENV ZED_SDK_MINOR=8

# Fix numpy issues
ENV OPENBLAS_CORETYPE AARCH64

# Install Python newer than 3.6
RUN apt-get update -y || true \
 && apt-get install -y ca-certificates software-properties-common && update-ca-certificates
RUN add-apt-repository ppa:deadsnakes/ppa \
 && apt-get update -y
RUN apt-get install python3.10 python3-pip python3-dev python3-setuptools -y

# I understand this is bad to do, but the ZEDSDK installs a bunch of
# packages into `python3`, so setting this to our desired version reduces
# duplicate installs
# RUN rm /usr/bin/python3 && ln -s /usr/bin/python3.10 /usr/bin/python3

#This environment variable is needed to use the streaming features on Jetson inside a container
ENV LOGNAME root
ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update || true && \
    apt-get install --no-install-recommends zstd lsb-release wget less udev sudo apt-transport-https -y && \
    echo "# R${L4T_MAJOR_VERSION} (release), REVISION: ${L4T_MINOR_VERSION}.${L4T_PATCH_VERSION}" > /etc/nv_tegra_release ; \
    python3 -m pip install cython wheel && \
    python3 -m pip install numpy && \
    apt-get remove --purge build-essential python3-dev -y && apt-get autoremove -y && \
    wget -q --no-check-certificate -O ZED_SDK_Linux.run https://download.stereolabs.com/zedsdk/${ZED_SDK_MAJOR}.${ZED_SDK_MINOR}/l4t${L4T_MAJOR_VERSION}.${L4T_MINOR_VERSION}/jetsons && \
    chmod +x ZED_SDK_Linux.run ; ./ZED_SDK_Linux.run -- silent runtime_only && \
    rm -rf /usr/local/zed/resources/* \
    rm -rf ZED_SDK_Linux.run && \
    rm -rf /var/lib/apt/lists/*

#This symbolic link is needed to use the streaming features on Jetson inside a container
RUN ln -sf /usr/lib/aarch64-linux-gnu/tegra/libv4l2.so.0 /usr/lib/aarch64-linux-gnu/libv4l2.so

WORKDIR /app

COPY requirements.txt requirements.txt

RUN python3 -m pip install -r requirements.txt

COPY . .

CMD ["python3", "vio.py"]