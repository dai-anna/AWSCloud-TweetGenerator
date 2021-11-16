import requests
import os


def test_hashtag_endpoint_live():
    access_token = os.environ.get("API_TOKEN")

    url = "https://api.twitter.com/1.1/trends/place.json?id=23424977"

    payload = {}
    headers = {
        "Authorization": "Bearer {}".format(access_token),
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    assert response.ok