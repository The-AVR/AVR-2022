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

COPY . .

RUN cp /app/mavlink/*.xml /usr/local/lib/python3.9/site-packages/pymavlink/dialects/v20/
RUN cp /app/mavlink/*.py /usr/local/lib/python3.9/site-packages/pymavlink/dialects/v20/

ENV MAVLINK20=1
ENV MAVLINK_DIALECT=bell

CMD ["python3", "-u", "fcc.py"]