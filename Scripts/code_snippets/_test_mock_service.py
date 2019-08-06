import requests

def test_mock_service():
    url = 'http://127.0.0.1:5000/json'    
    resp = requests.get(url)           
    assert resp.status_code == 200
    print(resp.text)