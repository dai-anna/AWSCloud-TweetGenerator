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
# print(os.system("ls -l"))

if os.getenv("IS_DOCKER") is not None:
    print(os.system("ls -l templates"))
    print("Running in Docker")
    templates = Jinja2Templates(directory="templates")
    from inference import finish_sentence, corpus
else:
    sys.path.append(".")
    from scripts.text_generator.inference import finish_sentence, corpus
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


def get_available_hashtags():
    with io.BytesIO() as f:
        bucket.download_fileobj("hashtags.txt", f)
        f.seek(0)
        hashtags = f.read().decode("utf-8").splitlines()
    return hashtags


def get_all_tweet_seeds():
    sep_tweets: list[str] = " ".join(corpus).split(" . ")
    tweet_seeds = [" ".join(tweet.split()[:4]) for tweet in sep_tweets if len(tweet.split()) > 6]
    return tweet_seeds


def get_inferred_tweet(seed_str: str = "I think that", selected_hashtag: str = None):
    """ Produces prediction and pretties up result. """

    if selected_hashtag is None:
        return "Please select a hashtag from the list!"
    result = finish_sentence(seed_str.split(), n=3, corpus=corpus, max_len=25)
    result = " ".join(result)
    result = result.replace(" ,", ",").replace(" .", ".")  # rm space around punctuation
    result = result.replace("  ", " ")  # rm double spaces
    result = result.replace(selected_hashtag.lower(), "")
    result = result + f" #{selected_hashtag}"
    result = result.replace("##", "#")  # rm double hashtags


    return result
########### INIT Environmet ##############
HASHTAGS = get_available_hashtags()
tweet_seeds = get_all_tweet_seeds()



##########################################



@app.get("/", response_class=HTMLResponse)
async def main_page(request: Request):
    result = None
    selected_topic = None
    try:
        print(request.query_params.get("userinput"))
        result = request.query_params.get("userinput")
        selected_topic = request.query_params.get("userinput")
    except:
        result = "Your tweet will appear here."
        selected_topic = HASHTAGS[0]

    # do inference
    try:
        seed = random.choice(tweet_seeds)
        result = get_inferred_tweet(seed, selected_hashtag=selected_topic)
    except Exception as e:
        result = f"[ERROR] Inference did not work :( [{e}]"


    params = {
        "request": request,  # do not change, has to be passed
        "hashtags": get_available_hashtags(),  # populates dropdown
        "selected_topic": selected_topic,  # populates dropdown
        "result": result,
    }

    return templates.TemplateResponse("index.html", params)
