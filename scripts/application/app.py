#%%
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os
import sys
import io
import boto3
import random
import re
import joblib
import tweepy
from collections import Counter

#%%
DATE_REGEX = re.compile(r"\d\d\d\d-\d\d-\d\d")

# Detect docker env and use different imports
if os.getenv("IS_DOCKER") is not None:
    templates = Jinja2Templates(directory="templates")
    from inference import finish_sentence
    from train import (
        get_most_current_date_in_s3,
        get_available_hashtags,
        get_corpora_for_hashtags,
    )
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


# -------------------------------- S3 Connection --------------------------------
s3 = boto3.resource(
    service_name="s3",
    region_name="us-east-1",
    aws_access_key_id=os.getenv("ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("SECRET_ACCESS_KEY"),
)
bucket = s3.Bucket(os.getenv("BUCKET_NAME"))

twitter_auth_keys = {
    "consumer_key": os.getenv("API_KEY"),
    "consumer_secret": os.getenv("API_KEY_SECRET"),
    "access_token": os.getenv("ACCESS_TOKEN"),
    "access_token_secret": os.getenv("ACCESS_TOKEN_SECRET"),
}


# -------------------------------- Functions --------------------------------
def get_all_tweet_seeds(hashtags: list[str]):
    """Generates list of all possible seeds (3-word sentence starts) from corpus"""

    tweet_seeds = dict()

    for hashtag in hashtags:
        sep_tweets: list[str] = " ".join(
            corpora.get(hashtag, "There is no data. There is no data.".split("c"))
        ).split(". ")
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
        corpus=corpora.get(
            selected_hashtag, "There is no data. There is no data.".split()
        ),
        max_len=20,
        proba_dict=models.get(selected_hashtag, {}),
    )
    result = " ".join(result)
    result = result.replace(" ,", ",").replace(" .", ".")  # rm space around punctuation
    result = result.replace("  ", " ")  # rm double spaces
    result = result.replace(selected_hashtag.lower(), "")
    result = result + f" #{''.join(selected_hashtag.split())}"
    result = result.replace("##", "#")  # rm double hashtags
    result = result.replace("&amp;", "&")  # rm double hashtags

    return result


def get_models_for_hashtags(hashtags: list[str], most_current_date: str):
    """Gets models for all hashtags for date. returns dict of (hashtag: model) mappings"""
    num_regex = re.compile(r"\/model_(?P<num>\d+).joblib")
    model_names = [
        obj.key
        for obj in bucket.objects.filter(Prefix=f"{most_current_date}/")
        if "model_" in obj.key
    ]
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


async def is_this_a_good_tweet(tweet: str):
    """Checks if tweet is a good tweet"""

    if len(tweet) > 280:
        print("Too long.")
        return False

    if len(tweet.split()) < 6:
        print("Too few words.")
        return False

    word_lens = [len(word) for word in tweet.split()]
    if sum(word_lens) / len(tweet.split()) < 4:
        print(f"Too short words.")
        return False

    counter = Counter(tweet.split())
    rel_freq = {word: counter[word] / sum(counter.values()) for word in counter}
    if any(freq > 0.2 for freq in rel_freq.values()):
        print("Too repetitive.")
        return False

    return True


def post_tweet(tweet: str):
    """Posts tweet to twitter. Use in moderation!"""

    twitter_auth_keys = {
        "consumer_key": os.getenv("API_KEY"),
        "consumer_secret": os.getenv("API_KEY_SECRET"),
        "access_token": os.getenv("ACCESS_TOKEN"),
        "access_token_secret": os.getenv("ACCESS_TOKEN_SECRET"),
    }

    auth = tweepy.OAuthHandler(
        twitter_auth_keys["consumer_key"], twitter_auth_keys["consumer_secret"]
    )
    auth.set_access_token(
        twitter_auth_keys["access_token"], twitter_auth_keys["access_token_secret"]
    )
    api = tweepy.API(auth)

    post_result = api.update_status(status=tweet)


# ---------------------- Init Environment --------------------------------
# HASHTAGS = ["a", "b", "c"]
most_current_date = get_most_current_date_in_s3()
# most_current_date = "2021-11-17"  # hardcode for experimenting
print(f"{most_current_date = }")
hashtags = get_available_hashtags(most_current_date)
corpora, _ = get_corpora_for_hashtags(
    hashtags, most_current_date
)  # we dont use the corpus numbers here
tweet_seeds: dict = get_all_tweet_seeds(hashtags)
models: dict = get_models_for_hashtags(hashtags, most_current_date)
# ------------------------------------------------------------------------


# -------------------------------- Routes --------------------------------
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
        "most_current_date": most_current_date,
    }

    return templates.TemplateResponse("index.html", params)


@app.get("/pull_new_model", status_code=200)
async def pull_new_model(request: Request):
    # these need to be global to overwrite the preexisting values ones
    global most_current_date
    global models
    global hashtags
    global corpora
    global tweet_seeds

    most_current_date = get_most_current_date_in_s3()
    print(f"{most_current_date = }")

    hashtags = get_available_hashtags(most_current_date)
    corpora, _ = get_corpora_for_hashtags(
        hashtags, most_current_date
    )  # we dont use the corpus numbers here
    tweet_seeds = get_all_tweet_seeds(hashtags)
    models = get_models_for_hashtags(hashtags, most_current_date)

    return {"message": "New models pulled.", "using_date": str(most_current_date)}


@app.get("/secret_endpoint_to_post_tweet", status_code=200, include_in_schema=False)
async def generate_and_post_tweet(request: Request):

    is_good = False
    n_trials = 0

    while not is_good:
        if n_trials > 20:
            tweet = "I'm sorry, I couldn't generate a good tweet today :( Check back tomorrow!"
            return {"message": "Could not post tweet."}
        tweet = get_inferred_tweet(selected_hashtag=hashtags[0])
        print(tweet)
        is_good = await is_this_a_good_tweet(tweet)
        print(is_good)
        n_trials += 1

    # post tweet
    post_tweet(tweet)

    return {"message": "Tweet posted.", "tweet": tweet}
