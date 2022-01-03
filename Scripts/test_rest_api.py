"""
Description:
Restful API testing framework example

Features:
    Common get/post function to:
    * Print every request and response in a API output file
    * Append common headers
    * Take care of request exception and non-20x response codes and return None, so you only need to care normal json response.
    
Install:
pip install -r requirements.txt

Run:
pytest

Python version: 3.6 or above
"""
from time import sleep
from datetime import datetime
import logging
from logging.handlers import RotatingFileHandler
import requests
import json
import os
# import ipdb
import inspect
import sys
from dotmap import DotMap

if sys.version_info < (3,6):
    raise Exception("Requires Python 3.6 or above.")

## Parameters
LOG_LEVEL = logging.INFO # DEBUG, INFO, WARNING, ERROR, CRITICAL
VALID_HTTP_RESP = (200, 201, 202)

# Assume project structure as below:
# Scripts - python scripts
# Logs - logs
# run.bat - batch script to run

# root_path is parent folder of Scripts folder (one level up)
root_path = os.path.dirname( os.path.dirname(os.path.realpath(__file__)) )

# %(levelname)7s to align 7 bytes to right, %(levelname)-7s to left.
common_formatter = logging.Formatter('%(asctime)s [%(levelname)-7s][ln-%(lineno)-3d]: %(message)s', datefmt='%Y-%m-%d %I:%M:%S')

# Note: To create multiple log files, must use different logger name.
def setup_logger(log_file, level=logging.INFO, name='', formatter=common_formatter):
    """Function setup as many loggers as you want."""
    handler = logging.FileHandler(log_file,mode='w') # default mode is append
    # Or use a rotating file handler
    # handler = RotatingFileHandler(log_file,maxBytes=1024, backupCount=5)
    handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    return logger
    
# default debug logger 
debug_log_filename = root_path + os.sep + 'Logs' + os.sep + 'debug.log'
log = setup_logger(debug_log_filename, LOG_LEVEL,'log')

# logger for API outputs
api_formatter = logging.Formatter('%(asctime)s: %(message)s', datefmt='%Y-%m-%d %I:%M:%S')
api_outputs_filename = root_path + os.sep + 'Logs' + os.sep + 'api_outputs.log'
log_api = setup_logger(api_outputs_filename, LOG_LEVEL,'log_api',formatter = api_formatter)

# pretty print Restful request to API log
# argument is request object 
def pretty_print_request(request):
    """
    Pay attention at the formatting used in this function because it is programmed to be pretty printed and may differ from the actual request.
    """
    log_api.info('{}\n{}\n\n{}\n\n{}\n'.format(
        '-----------Request----------->',
        request.method + ' ' + request.url,
        '\n'.join('{}: {}'.format(k, v) for k, v in request.headers.items()),
        request.body)
        )

# pretty print Restful response to API log
# argument is response object         
def pretty_print_response(response):
    log_api.info('{}\n{}\n\n{}\n\n{}\n'.format(
        '<-----------Response-----------',
        'Status code:' + str(response.status_code),
        '\n'.join('{}: {}'.format(k, v) for k, v in response.headers.items()),
        response.text)
        )        

        
def pretty_print_request_json(request):
    log_api.info('{}\n{}\n\n{}\n\n{}\n'.format(
        '-----------Request----------->',
        request.method + ' ' + request.url,
        '\n'.join('{}: {}'.format(k, v) for k, v in request.headers.items()),
        json.dumps(json.loads(request.body),indent=4))
        )
        
# argument is response object 
# display body in json format explicitly with expected indent. Actually most of the time it is not very necessary because body is formatted in pretty print way.    
def pretty_print_response_json(response):
    """ pretty print response in json format. 
        If failing to parse body in json format, print in text.
    """
    try:
        resp_data = response.json()
        resp_body = json.dumps(resp_data,indent=4)
    # if .json() fails, ValueError is raised, take text format
    except ValueError:
        resp_body = response.text
        
    log_api.info('{}\n{}\n\n{}\n\n{}\n'.format(
        '<-----------Response-----------',
        'Status code:' + str(response.status_code),
        '\n'.join('{}: {}'.format(k, v) for k, v in response.headers.items()),
        resp_body
        ))

def dict_to_ini(dict_var, file=None):
    """ Covert a dict to ini file format

    Example Input    
    -------------    
    {
        "name": {
            "firstname": "Peter",
            "secondname": "Xie"
        },
        "scores": [100,99],
        "age": 30
    }

    Example Output
    --------------
    name.firstname = Peter
    name.secondname = Xie
    scores[0] = 100
    scores[1] = 99
    age = 30
    """
    ini_contents = ''

    def iterate_dict(var, prefix=None):
        """ 
        """            
        # recursive if dict
        if isinstance(var,dict):
            for k,v in var.items():
                if prefix is None:
                    new_prefix = k  # e.g. age
                else:
                    new_prefix = prefix + '.' + k # e.g. name.firstname
                iterate_dict(v, new_prefix)
        elif isinstance(var,list):
            for index, value in enumerate(var):
                assert prefix is not None # Invalid to start from something like iterate_dict([1,2], None)
                new_prefix = '%s[%d]' % (prefix, index) # e.g. scores[0]
                iterate_dict(value, new_prefix)                             
        else:                
            this_item = "%s = %s" % (prefix, var) 
            nonlocal ini_contents
            ini_contents += this_item + '\n'
            
    assert isinstance(dict_var, dict)
    iterate_dict(dict_var, None)
    if file is not None:
        with open(file, 'w') as f:
            f.write(ini_contents)
            
    return ini_contents

class TestAPI:
    """
    Test Restful HTTP API examples. 
    """ 
    def setup_class(cls):
        log.debug('To load test data.')    
    
    # post with headers, json body
    def test_post_headers_body_json(self):
        payload = {'key1': 1, 'key2': 'value2'}
        # No need to specify common headers as it is taken cared of by common self.post() function.
        # headers = {'Content-Type': 'application/json' } 
        
        # convert dict to json by json.dumps() for body data. It is risky to use str(payload) 
        # to convert because json format must use double quotes ("")
        url = 'http://httpbin.org/post'
        resp = self.post(url, data = json.dumps(payload,indent=4))      
        assert resp != None
        # self.post converts the return to json if it is not None
        assert resp['url'] == url
        assert resp['json']['key1'] == 1
        # dot fashion with DotMap
        assert DotMap(resp).json.key1 == 1        
        log.info('Test %s passed.' % inspect.stack()[0][3])
        """ Request HTTP body:
        {   "key1": 1, 
            "key2": "value2"
        }

        Response body:
        {
        "args": {},
        "data": "{\n    \"key1\": 1,\n    \"key2\": \"value2\"\n}",
        "files": {},
        "form": {},
        "headers": {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate",
            "Content-Length": "39",
            "Host": "httpbin.org",
            "User-Agent": "python-requests/2.22.0"
        },
        "json": {
            "key1": 1,
            "key2": "value2"
        },
        "origin": "103.115.210.48, 103.115.210.48",
        "url": "https://httpbin.org/post"
        }
        """   

    # post with normal data
    def test_post_normal_body(self):
        payload = {'key1': 1, 'key2': 'value2'} 
        url = 'http://httpbin.org/post'
        resp = self.post(url, data = payload, amend_headers=False)      
        assert resp != None
        log.info('Test %s passed.' % inspect.stack()[0][3])
        """ Request HTTP body:
        key1=1&key2=value2
        """    
        
    # get with authentication
    def test_get_auth_httpbin(self):        
        log.info('Calling %s.' % inspect.stack()[0][3])       
        username = 'user1'
        password = 'password1'
        
        url = f'http://httpbin.org/basic-auth/{username}/{password}'        
        resp = self.get(url, auth = (username,password))
        assert resp != None
        assert resp["authenticated"] == True
        log.info('Test %s passed.' % inspect.stack()[0][3])        
        """ json response
        {
        "authenticated": true, 
        "user": "user1"
        }
        """    
    
    # To run this test using Flask mocking service,
    # First, rename this method from disabled_test_mock_service to test_mock_service. 
    # Second, start mock service first: python flask_mock_service.py
    # Then, run the tests, i.e. pytest.
    # def disabled_test_mock_service(self):
    def test_mock_service(self):    
        log.info('Calling %s.' % inspect.stack()[0][3])               
        url = 'http://127.0.0.1:5000/hello'    
        resp = self.get(url)
        assert resp != None
        assert resp["code"] == 1
        log.info('Test %s passed.' % inspect.stack()[0][3])        
        """ json response
        {
        "code": 1,
        "message": "Hello, World!"
        }
        """

    # Any endpoints with expected response status code and body data set in the request headers.
    # def disabled_test_mock_service_dynamic(self):      
    def test_mock_service_dynamic(self):    
        log.info('Calling %s.' % inspect.stack()[0][3])               
        url = 'http://127.0.0.1:5000/anyendpoint'   
        response_code = '202'
        response_body = '{"code": 0, "message": "all good"}'
        headers = {'response_code': response_code, 'response_body': response_body}    
        resp = self.get(url, headers = headers)       
        assert resp != None
        assert resp["code"] == 0
        log.info('Test %s passed.' % inspect.stack()[0][3])        
        """ response
        202 
        
        {"code": 0, "message": "all good"}
        """

    def post(self, url, data, headers={}, verify=False, amend_headers=True):
        """
        common request post function with below features, which you only need to take care of url and body data:
            - append common headers
            - print request and response in API log file
            - Take care of request exception and non-20x response codes and return None, so you only need to care normal json response.
            - arguments are the same as requests.post, except amend_headers.
        
        verify: False - Disable SSL certificate verification 
        """
        
        # append common headers if none
        headers_new = headers
        if amend_headers == True:
            if 'Content-Type' not in headers_new:
                headers_new['Content-Type']=r'application/json'
            if 'User-Agent' not in headers_new:
                headers_new['User-Agent']='Python Requests'
                
        # send post request
        try:
            resp = requests.post(url, data=data, headers=headers_new, verify=verify)
        except Exception as ex:
            log.error('requests.post() failed with exception: %s' % str(ex))
            return None        

        # pretty request and response into API log file
        # Note: request print is common instead of checking if it is JSON body. So pass pretty formatted json string as argument to the request for pretty logging. 
        pretty_print_request(resp.request)    
        pretty_print_response_json(resp)
        
        # This returns caller function's name, not this function post.
        caller_func_name = inspect.stack()[1][3]        
        if resp.status_code not in VALID_HTTP_RESP:
            log.error('%s failed with response code %s.' %(caller_func_name,resp.status_code))
            return None
        return resp.json()

    def get(self, url, headers={}, auth = None, verify=False):
        """
        common request get function with below features, which you only need to take care of url:
            - print request and response in API log file
            - Take care of request exception and non-20x response codes and return None, so you only need to care normal json response.
            - arguments are the same as requests.get
        
        verify: False - Disable SSL certificate verification 
        """
        try:
            if auth == None:
                resp = requests.get(url, headers=headers, verify=verify)
            else:
                resp = requests.get(url, headers=headers, auth=auth, verify=verify)
        except Exception as ex:
            log.error('requests.get() failed with exception: %s' % str(ex))
            return None
        
        # pretty request and response into API log file
        pretty_print_request(resp.request)    
        pretty_print_response_json(resp)
        
        # This return caller function's name, not this function post.
        caller_func_name = inspect.stack()[1][3]        
        if resp.status_code not in VALID_HTTP_RESP:
            log.error('%s failed with response code %s.' %(caller_func_name,resp.status_code))
            return None
        return resp.json()


if __name__ == '__main__':
    # self test
    var = {
        "name": {
            "firstname": "Peter",
            "secondname": "Xie"
        },
        "scores": [{"k1": 1},{"k1":"v2"}],
        "age": 22
    }
    print(dict_to_ini(var,"a.ini"))