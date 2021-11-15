FROM python:3.9-slim-buster

WORKDIR /app

COPY ./gethashtags.py /app/gethashtags.py
COPY ./requirements_hashtagscrape.txt /app/requirements_hashtagscrape.txt

RUN pip install --upgrade pip \
    && pip install -r /app/requirements_hashtagscrape.txt

ENTRYPOINT ["python"]
CMD ["/app/gethashtags.py"]