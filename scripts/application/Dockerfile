FROM python:3.9-slim-buster

WORKDIR /application

COPY application/ /application
RUN pip install --no-cache-dir -r /application/requirements_frontend.txt
COPY text_generator/inference.py /application/inference.py
COPY text_generator/train.py /application/train.py

ENV IS_DOCKER=1

RUN python -m nltk.downloader gutenberg \
    && python -m nltk.downloader punkt

ENTRYPOINT uvicorn app:app --host 0.0.0.0 --port 8080