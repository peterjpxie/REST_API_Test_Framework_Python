def request(self, method, url, headers={}, data=None, 
    amend_headers=True, verify=False, **kwargs):
    """Common request function, which can be used for any request methods such as post, get, delete, put etc."""
    import requests
    # append common headers
    headers_new = headers
    if amend_headers is True:
        headers_new["Content-Type"] = "application/json"
    
    # send request
    try:
        resp = requests.request(
            method, url, headers=headers_new, data=data, verify=verify, **kwargs
        )
    except Exception as ex:
        log.error("requests.request() failed with exception: %s" % str(ex))
        return None

    # pretty request and response into API log file
    pretty_print_request(resp.request)
    pretty_print_response_json(resp)

    if resp.status_code not in VALID_HTTP_RESP:
        log.error("request failed with response code %s." % resp.status_code)
        return None
    return resp.json()