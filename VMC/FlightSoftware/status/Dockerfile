FROM nvcr.io/nvidia/l4t-ml:r32.6.1-py3
#FROM docker.io/library/python:3.9-buster

ENV OPENBLAS_CORETYPE=ARMV8


RUN apt update && apt install software-properties-common -y
RUN add-apt-repository ppa:deadsnakes/ppa && apt install python3.8 -y && apt install python3.8-dev -y
RUN update-alternatives --install /usr/bin/python python /usr/bin/python2.7 1
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.8 2
RUN update-alternatives --auto python
RUN python --version
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.6 1
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.8 2
RUN update-alternatives --auto python3
RUN python3 --version

WORKDIR /app
RUN ["apt-get", "update"]
RUN ["apt-get", "install", "-y", "vim"]
RUN groupadd -g 999 gpio
RUN cd ~ && git clone https://github.com/NVIDIA/jetson-gpio.git && cp ~/jetson-gpio/lib/python/Jetson/GPIO/99-gpio.rules /etc/udev/rules.d
COPY requirements.txt requirements.txt
RUN python -m pip install setuptools && python -m pip install wheel
RUN python -m pip install -r requirements.txt

COPY . .


CMD ["python", "status.py"]
#CMD tail -f /dev/null
