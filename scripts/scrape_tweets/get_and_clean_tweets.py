import datetime
import os
import boto3
import pandas as pd
import re
import tempfile
import logging
import requests
import time

logging.basicConfig(
    format="[%(levelname)s] %(asctime)s - %(message)s",
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("log_get_and_clean_tweets.log"),
    ],
)

today = datetime.date.today()
# today = "2022-01-03"  # Hardcode


ROOT_DIR = "./"


s3 = boto3.resource(
    service_name="s3",
    region_name="us-east-1",
    aws_access_key_id=os.getenv("ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("SECRET_ACCESS_KEY"),
)


bucket = s3.Bucket(os.getenv("BUCKET_NAME"))


def download_hashtag_file():
    """Downloads hashtags file from s3"""
    bucket.download_file(f"{today}/hashtags.txt", "hashtags.txt")
    logging.info("Hashtags fetched from S3.")


def pull_tweets_for_hashtag(hashtag, n_tweets: int = 100):
    """
    Pull tweets using Twitter API.
    IMPORTANT: Supply your own Twitter API Bearer Token as the API_TOKEN environment variable.
    """

    result_list = []

    url = "https://api.twitter.com/2/tweets/search/recent"
    headers = {
        "Authorization": f"Bearer {os.environ['API_TOKEN']}",
    }

    params = {
        "query": f"{hashtag} lang:en -is:retweet",
        "max_results": 100,  # min: 10, max: 100
    }

    ii = 0
    n_failed = 0

    while len(result_list) < n_tweets:
        if n_failed > 5:
            print("[ERROR] Too many failed requests. Exiting.")
            break

        print(f"[INFO] Sending request {ii}")
        try:
            response = requests.request("GET", url, headers=headers, params=params)
            response_json = response.json()
            result_list = result_list + response_json["data"]
            params["next_token"] = response_json["meta"]["next_token"]
            # print(
            #     f"[INFO] Received {len(result_list)} tweets so far.\n\t--> Head: {response_json['data'][0]['text']}"
            # )
        except Exception as e:
            n_failed += 1
            print(
                f"[ERROR] in this request. Skipping it (missing {params.get('max_results')} tweets)"
            )
            print(response.status_code)
            print(response.json())
            print(e)
        finally:
            ii += 1
            time.sleep(0.2)

    result_df = pd.DataFrame(result_list)

    return result_df.rename({'text': 'tweet'}, axis=1)

def scrape_tweets_from_hashtags(hashtag_file_path: str = "hashtags.txt"):
    """ Given a hashtag.txt file, scrape tweets from Twitter API and save them to a local csv. """
    with open(hashtag_file_path) as f:
        trends_ls = f.readlines()
        trends_ls = [line.rstrip() for line in trends_ls]

    for idx, trend in enumerate(trends_ls):
        trend = trend.lower()  # .strip("#").replace(" ", "")  # lets keep spaces
        logging.info(f"Starting {idx}: {trend} scrape")


        result_df = pull_tweets_for_hashtag(trend, n_tweets=1000)
        result_df.to_csv(f"apicall_output_{idx}.csv", index=False)

        logging.info(f"Finished {idx}: {trend} scrape")


###############################################


def load_files(filenames: list[str], lines: list[str]):
    """ Load local files """
    for f in filenames:
        if f.startswith("apicall_output"):
            tag = lines[int(re.findall("\d+", f)[0])]
            tag_idx = int(re.findall("\d+", f)[0])

            df = pd.read_csv(f, sep=",")

            df["tag"] = tag.strip("#")
            df["tag_idx"] = tag_idx

            yield df


def clean_tweets_df(all_tweets_raw: pd.DataFrame):
    """Cleans tweets data frame. It should have the column `tweets`."""
    url_mentions = re.compile(r"(@\S+) | (https?:\/\/.+)")

    all_tweets_raw["tweet"] = (
        all_tweets_raw["tweet"].str.encode("ascii", "ignore").str.decode("utf-8")
    )
    all_tweets_raw["tweet"] = all_tweets_raw["tweet"].replace(
        url_mentions, "", regex=True
    )
    all_tweets_raw["tweet"] = all_tweets_raw["tweet"].replace("#", "", regex=True)

    return all_tweets_raw


def get_tweets_and_clean():
    with open(f"hashtags.txt") as f:
        lines = f.readlines()
        lines = [line.rstrip() for line in lines]

    tweet_files = os.listdir()
    all_tweets_raw = pd.concat(load_files(tweet_files, lines))
    all_tweets_raw = clean_tweets_df(all_tweets_raw)

    logging.info(f"Starting Clean S3 upload")
    for idx in all_tweets_raw["tag_idx"].unique():
        with tempfile.TemporaryFile() as fp:
            export = all_tweets_raw.loc[
                all_tweets_raw["tag_idx"] == idx, "tweet"
            ].to_list()
            fp.writelines([str.encode(x + "\n") for x in export])
            fp.seek(0)
            bucket.upload_fileobj(fp, f"{today}/clean_out_{idx}.txt")
    logging.info(f"Ending Clean S3 upload")


if __name__ == "__main__":
    download_hashtag_file()
    scrape_tweets_from_hashtags()
    get_tweets_and_clean()
