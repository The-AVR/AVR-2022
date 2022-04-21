FROM docker.io/library/python:3.9-buster

WORKDIR /app

RUN apt-get update \
 && apt-get install -y udev \
 && git clone https://github.com/NVIDIA/jetson-gpio.git \
 && cp jetson-gpio/lib/python/Jetson/GPIO/99-gpio.rules /etc/udev/rules.d

WORKDIR /app

RUN apt-get update \
    && apt-get install -y udev \
    && git clone https://github.com/NVIDIA/jetson-gpio.git \
    && cp jetson-gpio/lib/python/Jetson/GPIO/99-gpio.rules /etc/udev/rules.d

COPY requirements.txt requirements.txt
RUN python -m pip install pip wheel --upgrade && \
    python -m pip install -r requirements.txt

COPY . .

CMD ["python3.9", "thermal.py"]
