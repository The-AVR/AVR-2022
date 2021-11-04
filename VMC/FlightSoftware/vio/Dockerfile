FROM nvcr.io/nvidia/l4t-ml:r32.6.1-py3

ENV LIBREALSENSE_VERSION=v2.49.0
ENV DEBIAN_FRONTEND=noninteractive
# https://stackoverflow.com/a/66057286
ENV OPENBLAS_CORETYPE=ARMV8

# Needed as some repo certs are expired in the base image
RUN apt-get update -y || true \
 && apt-get install -y ca-certificates && update-ca-certificates
RUN apt update -y
RUN apt install -y \
    git \
    libssl-dev \
    libusb-1.0-0-dev \
    libusb-dev \
    usbutils \
    pkg-config \
    build-essential \
    cmake \
    libgtk-3-dev \
    libglfw3-dev \
    libgl1-mesa-dev \
    libglu1-mesa-dev \
    software-properties-common
RUN add-apt-repository -y ppa:deadsnakes/ppa
RUN apt update
RUN apt install -y \
    python3.8 \
    python3.8-dev \
    python3-setuptools \
    python3-pip

WORKDIR /

RUN git clone https://github.com/IntelRealSense/librealsense --recurse-submodules \
 && cd librealsense \
 && git pull origin $LIBREALSENSE_VERSION \
 && git submodule update --init --recursive \
 && git checkout $LIBREALSENSE_VERSION

RUN mkdir -p /librealsense/build \
 && cd /librealsense/build \
 && cmake .. \
    -DBUILD_GRAPHICAL_EXAMPLES=false \
    -DFORCE_RSUSB_BACKEND=true \
    -DBUILD_EXAMPLES=true \
    -DBUILD_WITH_CUDA=true \
    -DCMAKE_BUILD_TYPE=release \
    -DBUILD_PYTHON_BINDINGS=true \
    -DPYTHON_EXECUTABLE=/usr/bin/python3.8 \
 && make -j3 \
 && make install

RUN cp /usr/local/lib/python3.8/pyrealsense2/* /usr/local/lib/python3.8/dist-packages/

RUN rm -rf /librealsense \
 && apt purge -y cmake \
 && apt autoremove -y

WORKDIR /app

COPY requirements.txt requirements.txt
RUN python3.8 -m pip install pip wheel --upgrade && \
    python3.8 -m pip install -r requirements.txt

COPY . .

CMD ["python3.8", "vio.py"]
