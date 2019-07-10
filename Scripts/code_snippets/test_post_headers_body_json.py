import requests
import json

def test_post_headers_body_json():
    url = 'http://httpbin.org/post'
    
    # No need to specify common headers as it is taken cared of by common self.post() function.
    headers = {'Content-Type': 'application/json' } 

    payload = {'key1': 1, 'key2': 'value2'}
    
    # convert dict to json by json.dumps() for body data. 
    resp = requests.post(url, data = json.dumps(payload,indent=4))       
    
    # Validate response, e.g. status code.
    assert resp.status_code == 200
    # print response body as text
    print(resp.text)