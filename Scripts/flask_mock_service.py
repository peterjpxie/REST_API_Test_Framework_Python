'''
Install:
pip install flask

Run with python CLI:
python flask_mock_service.py

Notes:
- Method is default as GET
'''


import os
# import ipdb
from flask import Flask, request, send_file, render_template
import json
from time import sleep

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/json', methods=['POST', 'GET'])
def test_json():
    sleep(0.2) # simulate network delay.
    return '{"code": 1, "message": "Hello, World!" }'

# Request headers
# http://flask.pocoo.org/docs/1.0/api/#flask.Request
# https://werkzeug.palletsprojects.com/en/0.15.x/datastructures/#werkzeug.datastructures.Headers
@app.route('/request_headers')
def test_req_headers():
    headers = request.headers
    
    # Get header values
    # get(key, default=None, type=None, as_bytes=False)
    # Return None if not found
    user_agent = headers.get('User-Agent')
    if user_agent is not None:
        return 'Header User-Agent in the request is %s.' % user_agent 
    else:
        return 'Header User-Agent does not exist in the request.'

# Request body content
# http://flask.pocoo.org/docs/1.0/api/#flask.Request
@app.route('/request_body', methods=['POST', 'GET'])
def test_req_body():
    # get_data(cache=True, as_text=False, parse_form_data=False)
    request_body = request.get_data()
    request_body = request_body.decode('utf-8') # decode if it is byte string b''
    return 'Request body content is\n%s' % request_body
    
    # Output for request with '{"key1":"value1","key2":2}':
    # Request body content is b'{"key1":"value1","key2":2}'

# Request body content as JSON    
# Parse and return the data as JSON. If the mimetype does not indicate JSON (application/json, see is_json), this returns None unless force is true.     
@app.route('/request_body_json', methods=['POST', 'GET'])
def test_req_body_json():
    # get_json(force=False, silent=False, cache=True)
    # Note: return is actually a dict
    
    # Note: is_json is changed to a property than a method.
    if request.is_json:
        return 'Request body content as json:\n%s' % json.dumps(request.get_json(cache=False),indent=4)
    else:
        return r'Request has no header application/json.'

@app.route('/request_body_force_json', methods=['POST', 'GET'])
def test_req_body_force_json():
    return 'Request body content forced as json:\n%s' % json.dumps(request.get_json(force=True, cache=False),indent=4)
    '''Output example:
    Request body content forced as json:
    {
        "key1": "value1",
        "key2": 2
    }
    '''

# get HTML form data https://www.w3schools.com/html/html_forms.asp
'''Raw forma data request:
content-type:"multipart/form-data; boundary=--------------------------706175916610648661144841"
content-length:278

----------------------------706175916610648661144841
Content-Disposition: form-data; name="username"

peter
----------------------------706175916610648661144841
Content-Disposition: form-data; name="password"

pwd
----------------------------706175916610648661144841--
'''
@app.route('/request_form_data', methods=['POST', 'GET'])
def test_req_form_data():
    return 'Request body:\n%s\n%s' % (request.form["username"],request.form["password"])

@app.route('/hello/')
@app.route('/hello/<name>')
def hello(name=None):
    return render_template('hello.html', name=name)

# return a file
# http://flask.pocoo.org/docs/1.0/api/#flask.send_file
@app.route('/download_file', methods=['POST', 'GET'])
@app.route('/download_file/<file>', methods=['POST', 'GET'])
def test_download_file(file='pytest.ini'):
    try:
        # return send_file('report.zip', as_attachment = True, attachment_filename='report.zip') # zip file
        return send_file(file, as_attachment = True, attachment_filename=file) # any file
    except Exception as e:
        return str(e)
    
# Run in HTTP  
# When debug = True, code is reloaded on the fly while saved
# app.run(host='127.0.0.1', port='5000', debug=True)    
app.run(host='0.0.0.0', port='5000', debug=True)    

# Run in HTTPS
# https://werkzeug.palletsprojects.com/en/0.15.x/serving/#quickstart
ssl_context_ = ('ssl_keys/key.crt', 'ssl_keys/key.key')
# app.run(host='127.0.0.1', port='5000', ssl_context=ssl_context_)
# output: Running on https://127.0.0.1:5001/
