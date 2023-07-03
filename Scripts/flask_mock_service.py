#!/usr/bin/env python3
"""
Install:
pip install flask

Run with python CLI:
python flask_mock_service.py

Notes:
- Method is default as GET
"""
from flask import Flask, request
import json
from time import sleep

app = Flask(__name__)


@app.route("/hello", methods=["POST", "GET"])
def mock_json():
    sleep(0.2)  # simulate network delay.
    return '{"code": 1, "message": "Hello, World!" }'


# Return dynamic status code and content based on request header data for any endpoints
#
# Sample request headers for expected return status code and body data:
#   response_code: 200
#   response_body: '{"code": 0, "message": "Hello, World!" }'
@app.before_request
def mock_dynamic():
    if not request.url.endswith("/hello"):
        headers = request.headers
        print("request.headers: ", headers)
        response_code = headers.get("Response-Code", 200)  # default to 200
        response_body = headers.get("Response-Body")
        if response_body is None:
            return '{"message": "response_body is not set." }'
        else:
            return response_body, int(response_code)


# Run in HTTP
# When debug = True, code is reloaded on the fly while saved
app.run(host="127.0.0.1", port=5000, debug=True)
# app.run(host='0.0.0.0', port=5000, debug=True)

# Run in HTTPS
# https://werkzeug.palletsprojects.com/en/0.15.x/serving/#quickstart
# ssl_context_ = ("ssl_keys/key.crt", "ssl_keys/key.key")
# app.run(host='127.0.0.1', port='5000', ssl_context=ssl_context_)
