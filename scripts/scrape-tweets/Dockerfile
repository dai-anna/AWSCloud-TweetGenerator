FROM python:3.9-slim-buster

WORKDIR /app

COPY ./gettweets.py /app/gettweets.py
COPY ./gettweets.py /app/cleantweets.py
COPY ./requirements_scrapetweets.txt /app/requirements_scrapetweets.txt

# install git for twint install
RUN apt-get update \
    && apt-get install -y --no-install-recommends git \
    && apt-get purge -y --auto-remove \
    && rm -rf /var/lib/apt/lists/*


RUN pip install --upgrade pip \
    && pip install -r /app/requirements_scrapetweets.txt


ENTRYPOINT ["python"]
CMD ["/app/gettweets.py", "/app/cleantweets.py"]