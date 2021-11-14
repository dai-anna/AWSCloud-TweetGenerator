FROM python:3.9-slim-buster

WORKDIR /application

COPY . /application
COPY templates /application/templates

RUN pip install --upgrade pip \
    && pip install -r /application/requirements_frontend.txt

ENTRYPOINT uvicorn app:app --host 0.0.0.0 --port 8080