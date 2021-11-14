FROM python:3.9-slim-buster

WORKDIR /app

COPY ./gethashtags.py /app/gethashtags.py
COPY ./gettweets.py /app/gettweets.py
COPY ./requirements_scrapetweets.txt /app/requirements.txt

# install git for twint install
RUN apt-get update \
    && apt-get install -y --no-install-recommends git \
    && apt-get purge -y --auto-remove \
    && rm -rf /var/lib/apt/lists/*


RUN pip install --upgrade pip \
    && pip install -r /app/requirements.txt


ENTRYPOINT ["python"]
CMD ["/app/gettweets.py"]