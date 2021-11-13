import os
import requests

access_token = os.environ.get("API_TOKEN")

url = "https://api.twitter.com/1.1/trends/place.json?id=23424977"

payload = {}
headers = {
    "Authorization": "Bearer {}".format(access_token),
    # "Cookie": 'guest_id=v1%3A163682872111862049; personalization_id="v1_NsvQEMNM+EmjK0Lkr4PpUw=="',
}


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
