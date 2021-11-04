FROM nvcr.io/nvidia/l4t-ml:r32.6.1-py3

ENV OPENBLAS_CORETYPE=CORTEXA57

# Needed as some repo certs are expired in the base image
RUN apt-get update -y || true \
 && apt-get install -y ca-certificates && update-ca-certificates
RUN apt-get update -y
RUN apt-get install -y \
    python3-pip \
    libssl-dev

WORKDIR /app

# Install paho C library
RUN git clone https://github.com/eclipse/paho.mqtt.c \
 && cd paho.mqtt.c \
 && git checkout v1.3.8 \
 && cmake -Bbuild -H. -DPAHO_ENABLE_TESTING=OFF -DPAHO_BUILD_STATIC=ON -DPAHO_WITH_SSL=ON -DPAHO_HIGH_PERFORMANCE=ON \
 && cmake --build build/ --target install \
 && ldconfig

# Install paho C++ library
RUN git clone https://github.com/eclipse/paho.mqtt.cpp \
 && cd paho.mqtt.cpp \
 && git checkout v1.2.0 \
 && cmake -Bbuild -H. -DPAHO_BUILD_STATIC=ON -DPAHO_BUILD_DOCUMENTATION=FALSE -DPAHO_BUILD_SAMPLES=FALSE \
 && cmake --build build/ --target install \
 && ldconfig

# Clone dependencies
RUN mkdir -p c/libraries

RUN git clone https://github.com/nlohmann/json c/libraries/json \
 && cd c/libraries/json \
 && git checkout v3.10.2

# RUN git clone https://github.com/NVIDIA-AI-IOT/isaac_ros_apriltag \
#  && cd isaac_ros_apriltag \
#  && git checkout v0.9.0-ea1 \
#  && cp -r isaac_ros_apriltag/nvapriltags/lib_aarch64_jetpack44 ../c/libraries/lib_aarch64_jetpack44

RUN wget https://developer.nvidia.com/isaac/download/third_party/april_tags_v5_jp44_nano-tar-xz \
 && tar -xf april_tags_v5_jp44_nano-tar-xz --directory c/libraries \
 && rm april_tags_v5_jp44_nano-tar-xz

# Build the april tag application
COPY c c
RUN mkdir -p c/build \
 && cd c/build \
 && cmake .. \
 && make -j4

COPY python/requirements.txt python/requirements.txt
RUN python3 -m pip install pip wheel --upgrade \
 && python3 -m pip install -r python/requirements.txt

COPY . .

CMD ["./docker-entrypoint.sh"]