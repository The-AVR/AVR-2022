FROM docker.io/library/python:3.9-buster

WORKDIR /app

COPY requirements.txt requirements.txt

RUN python -m pip install pip wheel --upgrade && \
    python -m pip install -r requirements.txt

RUN apt-get update && apt-get install -y udev
RUN cp /usr/local/lib/python3.9/site-packages/Jetson/GPIO/99-gpio.rules /etc/udev/rules.d

COPY . .

CMD ["python3.9", "thermal.py"]
