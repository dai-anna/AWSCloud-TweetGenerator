import pandas as pd
import os
import re
import boto3
import tempfile

ROOT_DIR = "./"

filePath = f"{ROOT_DIR}hashtags.txt"

if os.path.exists(filePath):
    os.remove(filePath)
else:
    pass

s3 = boto3.resource(
    service_name="s3",
    region_name="us-east-1",
    aws_access_key_id=os.getenv("ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("SECRET_ACCESS_KEY"),
)


bucket = s3.Bucket("exp-noahgift")
bucket.download_file("hashtags.txt", f"{ROOT_DIR}hashtags.txt")
print("[INFO] Hashtags fetched from S3.")

with open(f"{ROOT_DIR}hashtags.txt") as file:
    lines = file.readlines()
    lines = [line.rstrip() for line in lines]

tweet_files = os.listdir()

def load_files(filenames):
    for file in filenames:
        if file.startswith('twint_out'):
            tag = lines[int(re.findall("\d+",file)[0])]
            tag_idx = int(re.findall("\d+",file)[0])
            df = pd.read_csv(file, sep=",", usecols = ['tweet','language'])
            df = df.loc[df['language']=='en'].copy()
            df.drop("language",axis=1,inplace=True)
            df["tag"] = tag.strip("#")
            df["tag_idx"] = tag_idx
            
            yield df
        
all_tweets_raw = pd.concat(load_files(tweet_files))
# all_tweets_raw.to_csv(f"{ROOT_DIR}raw_tweets.csv")

emoji_pattern = re.compile("["
    u"\U0001F600-\U0001F64F"  # emoticons
    u"\U0001F300-\U0001F5FF"  # symbols & pictographs
    u"\U0001F680-\U0001F6FF"  # transport & map symbols
    u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
    u"\U00002702-\U000027B0"
    u"\U000024C2-\U0001F251"
    "]+", flags=re.UNICODE)

url_mentions = re.compile(r'(@\S+) | (https?:\/\/.+)')

all_tweets_raw["tweet"] = all_tweets_raw["tweet"].replace(emoji_pattern, '', regex=True)
all_tweets_raw["tweet"] = all_tweets_raw["tweet"].replace(url_mentions, '', regex=True)
all_tweets_raw["tweet"] = all_tweets_raw["tweet"].replace("#", '', regex=True)


# for idx in all_tweets_raw["tag_idx"].unique():
#     df = all_tweets_raw.loc[all_tweets_raw["tag_idx"]==idx].copy()
#     df = df["tweet"]

with tempfile.TemporaryFile() as fp:
    all_tweets_raw.to_csv(fp)
    fp.seek(0)
    bucket.upload_fileobj(fp, "trash.csv")

# bucket.upload_file(f"clean_out_{idx}.csv", bucket)



# print(all_tweets_raw.head())