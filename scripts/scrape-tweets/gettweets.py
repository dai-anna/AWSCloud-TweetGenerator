import twint
import datetime
from gethashtags import get_hashtags
import os
import boto3

trends_ls = get_hashtags()
print(trends_ls)

s3 = boto3.resource(
    service_name="s3",
    region_name="us-east-1",
    aws_access_key_id=os.getenv("ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("SECRET_ACCESS_KEY"),
)

bucket = s3.Bucket("exp-noahgift")

for idx, trend in enumerate(trends_ls):
    trend = trend.strip("#")
    c = twint.Config()
    c.Search = "#"+trend  # your search here
    c.Lang = "en"
    c.Since = (datetime.datetime.now() - datetime.timedelta(minutes=30)).strftime("%Y-%m-%d %H:%M:%S")
    c.Until = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    c.Store_csv = True
    c.Output = f"twint_out_{idx}.csv"
    print(f"[INFO] Starting {idx}: {trend} scrape")
    twint.run.Search(c)
    print(f"[INFO] Finished {idx}: {trend} scrape")
    print(f"[INFO] Starting S3 upload")
    bucket.upload_file(f"twint_out_{idx}.csv", f"twint_out_{idx}.csv")
    print(f"[INFO] Finished S3 upload")


