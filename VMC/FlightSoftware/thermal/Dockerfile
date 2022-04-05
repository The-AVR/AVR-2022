FROM nvcr.io/nvidia/l4t-ml:r32.6.1-py3
#FROM docker.io/library/python:3.9-buster

ENV OPENBLAS_CORETYPE=ARMV8

RUN apt-get update -y || true \
 && apt-get install -y ca-certificates software-properties-common && update-ca-certificates

# Install Python newer than 3.6
RUN add-apt-repository ppa:deadsnakes/ppa \
 && apt-get update -y

RUN add-apt-repository ppa:deadsnakes/ppa 

RUN apt-get install -y \
    python3.9 \
    python3.9-dev \
    python3.9-distutils \
    python3-pip \
    libssl-dev
RUN python3.9 -m pip install pip wheel setuptools --upgrade

WORKDIR /app
RUN ["apt-get", "update"]
RUN ["apt-get", "install", "-y", "vim"]
RUN groupadd -g 999 gpio
RUN cd ~ && git clone https://github.com/NVIDIA/jetson-gpio.git && cp ~/jetson-gpio/lib/python/Jetson/GPIO/99-gpio.rules /etc/udev/rules.d
COPY requirements.txt requirements.txt
RUN python3.9 -m pip install setuptools && python3.9 -m pip install wheel
RUN python3.9 -m pip install -r requirements.txt

COPY . .


CMD ["python3.9", "thermal.py"]
