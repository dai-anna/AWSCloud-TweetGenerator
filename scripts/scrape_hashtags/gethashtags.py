import os
import requests
import tempfile
import boto3
import datetime

today = datetime.date.today()

access_token = os.environ.get("API_TOKEN")
print(f"[INFO] Using access_token={access_token}")

url = "https://api.twitter.com/1.1/trends/place.json?id=23424977"

payload = {}
headers = {
    "Authorization": "Bearer {}".format(access_token),
    # "Cookie": 'guest_id=v1%3A163682872111862049; personalization_id="v1_NsvQEMNM+EmjK0Lkr4PpUw=="',
}

s3 = boto3.resource(
    service_name="s3",
    region_name="us-east-1",
    aws_access_key_id=os.getenv("ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("SECRET_ACCESS_KEY"),
)

bucket = s3.Bucket(os.getenv("BUCKET_NAME"))


def get_hashtags():
    """Scrapes to 10 trending hashtags in the US."""
    response = requests.request("GET", url, headers=headers, data=payload)

    if not response.ok:
        print(f"[ERROR] Request to Twitter answered with {response.status_code}")
        print(response.text)

    tweet_data = response.json()

    trends_ls = []

    for i in range(0, 10):
        try:
            trends_ls.append(tweet_data[0]["trends"][i]["name"])
        except KeyError:
            print("[ERROR] Unexpected JSON structure. Got JSON:")
            print(tweet_data)
            # print(tweet_data[0]["trends"][i]["name"])
    assert len(trends_ls) == 10
    print("[INFO] Fetched all ten hashtags.")

    with tempfile.TemporaryFile() as fp:
        fp.writelines([str.encode(x + "\n") for x in trends_ls])
        fp.seek(0)
        bucket.upload_fileobj(fp, f"{today}/hashtags.txt")

    print("[INFO] Uploaded hashtags to S3.")

    return trends_ls

if __name__ == "__main__":
    get_hashtags()

