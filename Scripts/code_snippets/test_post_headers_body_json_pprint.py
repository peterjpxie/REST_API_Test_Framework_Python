import requests
import json

def pretty_print_request(request):
    print( '\n{}\n{}\n\n{}\n\n{}\n'.format(
        '-----------Request----------->',
        request.method + ' ' + request.url,
        '\n'.join('{}: {}'.format(k, v) for k, v in request.headers.items()),
        request.body)
    )

def pretty_print_response(response):
    print('\n{}\n{}\n\n{}\n\n{}\n'.format(
        '<-----------Response-----------',
        'Status code:' + str(response.status_code),
        '\n'.join('{}: {}'.format(k, v) for k, v in response.headers.items()),
        response.text)
    )         
    
def test_post_headers_body_json():
    url = 'https://httpbin.org/post'
    
    # Additional headers.
    headers = {'Content-Type': 'application/json' } 

    # Body
    payload = {'key1': 1, 'key2': 'value2'}
    
    # convert dict to json by json.dumps() for body data. 
    resp = requests.post(url, data = json.dumps(payload,indent=4))       
    
    # Validate response headers and body contents, e.g. status code.
    assert resp.status_code == 200
    resp_body = resp.json()
    assert resp_body['url'] == url
    
    # print full request and response
    pretty_print_request(resp.request)
    pretty_print_response(resp)
     