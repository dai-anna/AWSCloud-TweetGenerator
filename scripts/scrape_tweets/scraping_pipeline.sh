#!/bin/bash
echo "Starting scraping gettweets.py" && \
python3 gettweets.py && \
wait

echo "Starting scraping cleantweets.py" && \
python3 cleantweets.py
wait