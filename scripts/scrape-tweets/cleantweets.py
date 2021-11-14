import pandas as pd
import os
import re
import boto3

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


print(all_tweets_raw.head())