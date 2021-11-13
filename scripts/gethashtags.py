import requests
import urllib
import json
import base64

consumer_key = "8XsH2uYa9wAPa34GMW8aCgxD5"
consumer_secret = "YYI6Rmn2VJGROknrqPOhjxQIS2HyBrFLHNtcb1mihT4EPbIm7m"

key_secret = "{}:{}".format(consumer_key, consumer_secret).encode("ascii")

b64_enc_key = base64.b64encode(key_secret)
b64_enc_key = b64_enc_key.decode("ascii")

base_url = "https://api.twitter.com/"
auth_url = "{}oauth2/token".format(base_url)
auth_headers = {
    "Authorization": "Basic {}".format(b64_enc_key),
    "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
}
auth_data = {"grant_type": "client_credentials"}

# auth_resp = requests.post(auth_url, headers=auth_headers, data=auth_data)
# print(auth_resp.status_code)
# access_token = auth_resp.json()["access_token"]

access_token = "AAAAAAAAAAAAAAAAAAAAAJoQBwEAAAAA6%2FY%2F4eP1ZzIGXSZADMti5tV7zYo%3D98wKPUdnSrxg7vkCotKt6EogqR7GkA5098TAfj1J9SqpiRdnnK"
trend_headers = {"Authorization": "Bearer {}".format(access_token)}

trend_params = {
    "id": 23424977,
}

trend_url = "https://api.twitter.com/1.1/trends/place.json"
trend_resp = requests.get(trend_url, headers=trend_headers, params=trend_params)

print("Response code:", trend_resp.status_code)

tweet_data = trend_resp.json()

for i in range(0, 10):
    print(tweet_data[0]["trends"][i]["name"])
