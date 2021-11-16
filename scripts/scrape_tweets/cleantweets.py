import pandas as pd
import os
import re
import boto3
import tempfile
import datetime

today = datetime.date.today()

ROOT_DIR = "./"

filePath = f"{ROOT_DIR}/hashtags.txt"

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


bucket = s3.Bucket(os.getenv("BUCKET_NAME"))
bucket.download_file(f"{today}/hashtags.txt", "hashtags.txt")
print("[INFO] Hashtags fetched from S3.")

with open(f"{ROOT_DIR}hashtags.txt") as f:
    lines = f.readlines()
    lines = [line.rstrip() for line in lines]

tweet_files = os.listdir()

def load_files(filenames):
    for f in filenames:
        if f.startswith('twint_out'):
            tag = lines[int(re.findall("\d+",f)[0])]
            tag_idx = int(re.findall("\d+",f)[0])
            df = pd.read_csv(f, sep=",", usecols = ['date', 'tweet', 'language'])
            df = df.loc[df['language']=='en'].copy()
            df.drop("language",axis=1,inplace=True)
            df["tag"] = tag.strip("#")
            df["tag_idx"] = tag_idx
            
            yield df
        
all_tweets_raw = pd.concat(load_files(tweet_files))
# all_tweets_raw.to_csv(f"{ROOT_DIR}raw_tweets.csv")

# no longer archiving separately
# print(f"[INFO] Starting Archive S3 upload")

# with tempfile.TemporaryFile() as fp:
#     all_tweets_raw.to_csv(fp, index = False)
#     fp.seek(0)
#     bucket.upload_fileobj(fp, f"archive/twint_out_{datetime.date.today()}.csv")
# print(f"[INFO] Ending Archive S3 upload")

url_mentions = re.compile(r'(@\S+) | (https?:\/\/.+)')

all_tweets_raw["tweet"] = all_tweets_raw["tweet"].str.encode('ascii', 'ignore').str.decode('utf-8')
all_tweets_raw["tweet"] = all_tweets_raw["tweet"].replace(url_mentions, '', regex=True)
all_tweets_raw["tweet"] = all_tweets_raw["tweet"].replace("#", '', regex=True)
# all_tweets_raw["tweet"].apply(lambda z: z.replace(z[-x:],"") if (x==len(all_tweets_raw["tag"])) and (z[-x:]==all_tweets_raw["tag"]))

print(f"[INFO] Starting Clean S3 upload")
for idx in all_tweets_raw["tag_idx"].unique():
    with tempfile.TemporaryFile() as fp:
        export = all_tweets_raw.loc[all_tweets_raw["tag_idx"]==idx,"tweet"].to_list()
        fp.writelines([str.encode(x + "\n") for x in export])
        fp.seek(0)
        bucket.upload_fileobj(fp, f"{today}/clean_out_{idx}.txt")
print(f"[INFO] Ending Clean S3 upload")
