from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Optional
import os
import sys
import io
import boto3
import random
import re

import joblib

DATE_REGEX = re.compile(r"\d\d\d\d-\d\d-\d\d")

# Detect docker env and use different imports
if os.getenv("IS_DOCKER") is not None:
    templates = Jinja2Templates(directory="templates")
    from inference import finish_sentence
    from train import get_most_current_date_in_s3, get_available_hashtags, get_corpora_for_hashtags
else:
    sys.path.append(".")
    from scripts.text_generator.inference import finish_sentence
    from scripts.text_generator.train import (
        get_most_current_date_in_s3,
        get_available_hashtags,
        get_corpora_for_hashtags,
    )

    print("Running locally")
    templates = Jinja2Templates(directory="scripts/application/templates")

app = FastAPI()


s3 = boto3.resource(
    service_name="s3",
    region_name="us-east-1",
    aws_access_key_id=os.getenv("ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("SECRET_ACCESS_KEY"),
)


bucket = s3.Bucket(os.getenv("BUCKET_NAME"))


def get_all_tweet_seeds(hashtags: list[str]):
    """Generates list of all possible seeds (3-word sentence starts) from corpus"""

    tweet_seeds = dict()

    for hashtag in hashtags:
        sep_tweets: list[str] = " ".join(corpora[hashtag]).split(". ")
        tweet_seeds[hashtag] = [
            " ".join(tweet.split()[:4]) for tweet in sep_tweets if len(tweet.split()) > 6
        ]
    return tweet_seeds


def get_inferred_tweet(selected_hashtag: str = None):
    """Produces prediction and pretties up result."""

    if selected_hashtag is None:
        return "Please select a hashtag from the list!"

    # print(f"{tweet_seeds = }")
    seed_str = random.choice(tweet_seeds[selected_hashtag])
    # print(f"Using seed: {seed_str}")

    result = finish_sentence(
        seed_str.split(),
        n=3,
        corpus=corpora[selected_hashtag],
        max_len=25,
        proba_dict=models[selected_hashtag],
    )
    result = " ".join(result)
    result = result.replace(" ,", ",").replace(" .", ".")  # rm space around punctuation
    result = result.replace("  ", " ")  # rm double spaces
    result = result.replace(selected_hashtag.lower(), "")
    result = result + f" #{''.join(selected_hashtag.split())}"
    result = result.replace("##", "#")  # rm double hashtags

    return result


def get_models_for_hashtags(hashtags: list[str]):
    num_regex = re.compile(r"\/model_(?P<num>\d+).joblib")
    model_names = [obj.key for obj in bucket.objects.all() if "model_" in obj.key]
    # print(f"Found the following models: {model_names}")

    models = dict()
    print(model_names)
    for model_name in model_names:
        try:
            number = int(num_regex.search(model_name)["num"])
        except ValueError:
            print(f"[ERROR] Could not decode number in file name, defaulting to zero.")
            number = 0

        # print(f"{number = }")

        try:
            with io.BytesIO() as f:
                bucket.download_fileobj(f"{model_name}", f)
                f.seek(0)
                models[hashtags[number]] = joblib.load(f)
        except Exception as e:
            print(f"Could not load model {model_name}")
            print(e)
            continue

    # print(corpora)
    return models


########### INIT Environmet ##############
# HASHTAGS = ["a", "b", "c"]
most_current_date = get_most_current_date_in_s3()
print(f"{most_current_date = }")
hashtags = get_available_hashtags(most_current_date)
corpora: dict = get_corpora_for_hashtags(hashtags)
tweet_seeds: dict = get_all_tweet_seeds(hashtags)
models: dict = get_models_for_hashtags(hashtags)
##########################################


@app.get("/", response_class=HTMLResponse)
async def main_page(request: Request):
    result = None
    selected_topic = None

    try:
        # print(request.query_params.get("userinput"))
        result = request.query_params.get("userinput")
        selected_topic = request.query_params.get("userinput")
    except:
        result = "Your tweet will appear here."
        selected_topic = hashtags[0]

    # do inference
    try:
        result = get_inferred_tweet(selected_hashtag=selected_topic)
    except Exception as e:
        result = f"[ERROR] Inference did not work :( [{e}]"

    params = {
        "request": request,  # do not change, has to be passed
        "hashtags": get_available_hashtags(most_current_date),  # populates dropdown
        "selected_topic": selected_topic,  # populates dropdown
        "result": result,
    }

    return templates.TemplateResponse("index.html", params)
