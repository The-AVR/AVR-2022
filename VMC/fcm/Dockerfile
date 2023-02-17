FROM docker.io/library/python:3.10 AS poetry-exporter

WORKDIR /work

COPY pyproject.toml pyproject.toml
COPY poetry.lock poetry.lock

RUN python -m pip install poetry \
 && poetry export -o requirements.txt

# grpcio only has aarch64 builds for python 3.10
FROM docker.io/library/python:3.10-bullseye

ENV MAVLINK20=1
ENV MAVLINK_DIALECT=bell

WORKDIR /app

RUN apt-get update -y
RUN apt-get install -y \
    gcc \
    g++ \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

COPY --from=poetry-exporter /work/requirements.txt requirements.txt
RUN python -m pip install pip wheel --upgrade \
 && python -m pip install -r requirements.txt

COPY src .

RUN chmod +x ./entrypoint.sh

ENTRYPOINT ["/bin/bash", "-l", "-c", "./entrypoint.sh"]
