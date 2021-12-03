#%%
import tweepy
import os


def main():
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

    tweet = "Hello world from the Twitter API!"
    post_result = api.update_status(status=tweet)


