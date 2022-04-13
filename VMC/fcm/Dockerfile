FROM docker.io/library/python:3.9-buster

WORKDIR /app

RUN apt-get update -y
RUN apt-get install -y \
    gcc \
    g++ \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.txt
RUN python -m pip install pip wheel --upgrade && \
    python -m pip install -r requirements.txt

COPY pymavlink* /app/

ENV MAVLINK20=1
ENV MAVLINK_DIALECT=bell

# need to install from source as it's difficult to generate a .whl file for ARM
RUN python -m pip install /app/pymavlink*.tar.gz

COPY . .

CMD ["python", "fcm.py"]
