FROM docker.io/stereolabs/zed:3.6-py-devel-jetson-jp4.6

WORKDIR /app

COPY requirements.txt requirements.txt

RUN python3 -m pip install pip wheel --upgrade &&
    python3 -m pip install -r requirements.txt

COPY . .
COPY ./*.conf /usr/local/zed/settings/

CMD ["python3", "vio-experimental.py"]
