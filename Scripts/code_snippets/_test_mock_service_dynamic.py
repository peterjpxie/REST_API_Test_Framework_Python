import requests

def test_mock_service_dynamic():
    url = 'http://127.0.0.1:5000/anypoint' 
    response_code = '202'
    response_body = '{"code": 0, "message": "all good"}'
    headers = {'response_code': response_code, 'response_body': response_body}     
    resp = requests.get(url, headers = headers)           
    assert resp.status_code == 202
    assert resp.json()["code"] == 0
    # print("Response: " + resp.text)