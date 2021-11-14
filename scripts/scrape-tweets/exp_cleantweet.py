#%%
import pandas as pd
import os
import re
import boto3

#%%
df = pd.read_csv("twint_out_1.csv", sep = ",")

#%%
df 

#%%
all_tweets_raw = pd.read_csv("raw_tweets.csv")
all_tweets_raw["tweet"]


#%%
emoji_pattern = re.compile("["
    u"\U0001F600-\U0001F64F"  # emoticons
    u"\U0001F300-\U0001F5FF"  # symbols & pictographs
    u"\U0001F680-\U0001F6FF"  # transport & map symbols
    u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
    u"\U00002702-\U000027B0"
    u"\U000024C2-\U0001F251"
    "]+", flags=re.UNICODE)

#%%
re.findall(r'(@\S+) | (https?:\/\/.+)', all_tweets_raw["tweet"])


#%%
all_tweets_raw["tweet"] = all_tweets_raw["tweet"].replace(emoji_pattern, '', regex=True)
all_tweets_raw["tweet"] = all_tweets_raw["tweet"].replace("#", '', regex=True)
all_tweets_raw["tweet"] = all_tweets_raw["tweet"].replace("#", '', regex=True)

#%%
all_tweets_raw["tweet"]



# %%
