#%%
import sys
import pandas as pd

sys.path.append(".")
from scripts.scrape_tweets.get_and_clean_tweets import clean_tweets_df


def test_tweet_cleaning():
    with open("tests/stub_data/example_tweet.txt", "r") as f:
        stub_tweet = f.read()

    df = pd.DataFrame({"tweet": [stub_tweet]})

    clean = clean_tweets_df(df)
    assert clean['tweet'].iloc[0] == "this is an awesome  af example TweEEt example testig ifitsnotautomateditsbroken"

test_tweet_cleaning()
