import twint
import datetime
# from gethashtags import get_hashtags
import os
import boto3
import datetime

today = datetime.date.today()

ROOT_DIR = "./"

filePath = f"{ROOT_DIR}hashtags.txt"

if os.path.exists(filePath):
    os.remove(filePath)
else:
    pass

# trends_ls = get_hashtags()
# print(trends_ls)

s3 = boto3.resource(
    service_name="s3",
    region_name="us-east-1",
    aws_access_key_id=os.getenv("ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("SECRET_ACCESS_KEY"),
)


bucket = s3.Bucket(os.getenv("BUCKET_NAME"))
bucket.download_file("hashtags.txt", f"{ROOT_DIR}{today}/hashtags.txt")
print("[INFO] Hashtags fetched from S3.")

with open(f"{ROOT_DIR}{today}/hashtags.txt") as file:
    trends_ls = file.readlines()
    trends_ls = [line.rstrip() for line in trends_ls]


for idx, trend in enumerate(trends_ls):
    trend = trend.strip("#")
    c = twint.Config()
    c.Search = "#" + trend  # your search here
    c.Lang = "en"
    c.Since = (datetime.datetime.now() - datetime.timedelta(minutes=10)).strftime(
        "%Y-%m-%d %H:%M:%S"
    )
    c.Until = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    c.Store_csv = True
    c.Output = f"twint_out_{idx}.csv"
    print(f"[INFO] Starting {idx}: {trend} scrape")
    twint.run.Search(c)
    print(f"[INFO] Finished {idx}: {trend} scrape")
    # print(f"[INFO] Starting S3 upload")
    # bucket.upload_file(f"twint_out_{idx}.csv", f"twint_out_{idx}.csv")
    # print(f"[INFO] Finished S3 upload")
