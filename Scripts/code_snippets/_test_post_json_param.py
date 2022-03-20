import requests
import json


def test_post_json_param():
    url = "https://httpbin.org/post"
    payload = {"key1": 1, "key2": "value2"}
    resp = requests.post(url, json=payload)
    print(resp.text)
