'''
Install:
pip install flask

Run with python CLI:
python flask_mock_service.py

Notes:
- Method is default as GET
'''
from flask import Flask, request
import json
from time import sleep

app = Flask(__name__)

@app.route('/hello', methods=['POST', 'GET'])
def mock_json():
    sleep(0.2) # simulate network delay.
    return '{"code": 1, "message": "Hello, World!" }'

# Return dynamic status code and content based on request header data for any endpoints
# Features:
# - Define only one route for all endpoints since we use <path:subpath>
# - Define only one function for all endpoints and test scenarios since we return based on request header data
# 
# Sample request headers for expected return status code and body data:
#   response_status_code: 200
#   response_data: '{"code": 0, "message": "Hello, World!" }'
@app.before_request
def mock_dynamic():
    if not request.url.endswith('/hello'):
        headers = request.headers
        response_status_code = headers.get('response_status_code', 200) # default to 200
        response_data = headers.get('response_data')
        if response_data is None:
            return '{"message": "response_data is not set." }'
        else:
            return response_data, int(response_status_code)        

    
# Run in HTTP  
# When debug = True, code is reloaded on the fly while saved
app.run(host='127.0.0.1', port='5000', debug=True)    
# app.run(host='0.0.0.0', port='5000', debug=True)    

# Run in HTTPS
# https://werkzeug.palletsprojects.com/en/0.15.x/serving/#quickstart
ssl_context_ = ('ssl_keys/key.crt', 'ssl_keys/key.key')
# app.run(host='127.0.0.1', port='5000', ssl_context=ssl_context_)
