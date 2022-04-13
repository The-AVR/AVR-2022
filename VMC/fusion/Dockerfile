FROM docker.io/library/python:3.9-buster

ENV OPENBLAS_CORETYPE=ARMV8

WORKDIR /app

COPY requirements.txt requirements.txt
RUN python -m pip install pip wheel --upgrade && \
    python -m pip install -r requirements.txt

COPY . .

CMD ["python", "fusion.py"]