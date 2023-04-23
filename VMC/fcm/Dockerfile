FROM docker.io/library/python:3.9-buster

#TODO - test removal of this.. dont like that it ties it to armv8 hardware
ENV OPENBLAS_CORETYPE=ARMV8 

WORKDIR /app

RUN apt-get update -y
RUN apt-get install -y \
    gcc \
    g++ \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# ENV OPENBLAS_CORETYPE=ARMV8 #TODO see if this is still necessary with new numpy

COPY requirements.txt requirements.txt
RUN python -m pip install pip wheel --upgrade && \
    python -m pip install -r requirements.txt


ENV MAVLINK20=1
ENV MAVLINK_DIALECT=bell

COPY . .

RUN chmod +x ./entrypoint.sh

ENTRYPOINT ["/bin/bash", "-l", "-c", "./entrypoint.sh"]
