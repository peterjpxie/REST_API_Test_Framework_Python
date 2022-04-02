def request(self, method, url, headers={}, data=None, 
    amend_headers=True, verify=False, **kwargs):
    """Common request function, return json response or None for any errors"""
    import requests
    # append common headers
    headers_new = headers
    if amend_headers is True:
        headers_new["Content-Type"] = "application/json"
    
    # send request
    try:
        resp = requests.request(method, url, headers=headers_new, data=data, verify=verify, **kwargs)
    except Exception as ex:
        return None

    # pretty request and response into log file
    pretty_print_request(resp.request)
    pretty_print_response_json(resp)

    if resp.status_code not in (200, 201, 202):
        return None
    return resp.json()