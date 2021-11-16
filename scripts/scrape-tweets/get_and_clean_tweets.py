import twint
import datetime
import os
import boto3
import pandas as pd
import re
import tempfile

today = datetime.date.today()

ROOT_DIR = "./"


s3 = boto3.resource(
    service_name="s3",
    region_name="us-east-1",
    aws_access_key_id=os.getenv("ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("SECRET_ACCESS_KEY"),
)


bucket = s3.Bucket(os.getenv("BUCKET_NAME"))
bucket.download_file(f"{today}/hashtags.txt", "hashtags.txt")
print("[INFO] Hashtags fetched from S3.")


def scrape_tweets_from_hashtags(hashtag_file_path: str = "hashtags.txt"):
    with open(hashtag_file_path) as f:
        trends_ls = f.readlines()
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


###############################################


def load_files(filenames, lines):
    for f in filenames:
        if f.startswith("twint_out"):
            tag = lines[int(re.findall("\d+", f)[0])]
            tag_idx = int(re.findall("\d+", f)[0])
            df = pd.read_csv(f, sep=",", usecols=["date", "tweet", "language"])
            df = df.loc[df["language"] == "en"].copy()
            df.drop("language", axis=1, inplace=True)
            df["tag"] = tag.strip("#")
            df["tag_idx"] = tag_idx

            yield df


def clean_tweets_df(all_tweets_raw: pd.DataFrame):
    url_mentions = re.compile(r"(@\S+) | (https?:\/\/.+)")

    all_tweets_raw["tweet"] = (
        all_tweets_raw["tweet"].str.encode("ascii", "ignore").str.decode("utf-8")
    )
    all_tweets_raw["tweet"] = all_tweets_raw["tweet"].replace(url_mentions, "", regex=True)
    all_tweets_raw["tweet"] = all_tweets_raw["tweet"].replace("#", "", regex=True)

    return all_tweets_raw


def get_tweets_and_clean():
    with open(f"hashtags.txt") as f:
        lines = f.readlines()
        lines = [line.rstrip() for line in lines]

    tweet_files = os.listdir()
    all_tweets_raw = pd.concat(load_files(tweet_files, lines))
    all_tweets_raw = clean_tweets_df(all_tweets_raw)

    print(f"[INFO] Starting Clean S3 upload")
    for idx in all_tweets_raw["tag_idx"].unique():
        with tempfile.TemporaryFile() as fp:
            export = all_tweets_raw.loc[all_tweets_raw["tag_idx"] == idx, "tweet"].to_list()
            fp.writelines([str.encode(x + "\n") for x in export])
            fp.seek(0)
            bucket.upload_fileobj(fp, f"{today}/clean_out_{idx}.txt")
    print(f"[INFO] Ending Clean S3 upload")


if __name__ == "__main__":
    scrape_tweets_from_hashtags()
    get_tweets_and_clean()
