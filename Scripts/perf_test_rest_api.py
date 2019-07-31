"""
Description:
Scale up REST API functional tests to performance tests using threading.

Note: 
requests module is synchronous and does not support asyncio to await for responses. 
Another option is to use aiohttp module, which uses asyncio for asynchrony. This option requires re-writing 
the API test functions, though they are quite like requests functions, and measuring the response time 
is not straight forward as requests.       

Features:


Python version: 3.7 or above
    
Install:
pip install -U requests ipdb

Run:


"""
from time import sleep
from datetime import datetime
import logging
from logging.handlers import RotatingFileHandler
import requests
import json
import os
import ipdb
import ast
import inspect
import random
# import asyncio
import sys

if sys.version_info < (3,7):
    raise Exception("Requires Python 3.7 or above.")

# Change log level to error to improve client performance.
LOG_LEVEL = logging.INFO # DEBUG, INFO, WARNING, ERROR, CRITICAL

# Assume project structure as below:
# Scripts - python scripts
# Logs - logs
# run.bat - batch script to run

# root_path is parent folder of Scripts folder (one level up)
root_path = os.path.dirname( os.path.dirname(os.path.realpath(__file__)) )

# %(levelname)7s to align 7 bytes to right, %(levelname)-7s to left.
# common_formatter = logging.Formatter('%(asctime)s [%(levelname)-7s][ln-%(lineno)-3d]: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
common_formatter = logging.Formatter('%(asctime)s [%(levelname)-7s][ln-%(lineno)-3d]: %(message)s')

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
# api_formatter = logging.Formatter('%(asctime)s: %(message)s', datefmt='%Y-%m-%d %I:%M:%S')
api_formatter = logging.Formatter('%(asctime)s: %(message)s')
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

# pretty print Restful request to API log
# argument is response object         
def pretty_print_response(response):
    log_api.info('{}\n{}\n\n{}\n\n{}\n'.format(
        '<-----------Response-----------',
        'Status code:' + str(response.status_code),
        '\n'.join('{}: {}'.format(k, v) for k, v in response.headers.items()),
        response.text
        ))        

        
# argument is request object
# display body in json format explicitly with expected indent. Actually most of the time it is not very necessary because body is formatted in pretty print way.    
def pretty_print_request_json(request):
    log_api.info('{}\n{}\n\n{}\n\n{}\n'.format(
        '-----------Request----------->',
        request.method + ' ' + request.url,
        '\n'.join('{}: {}'.format(k, v) for k, v in request.headers.items()),
        json.dumps(ast.literal_eval(request.body),indent=4))
        )
        
# argument is response object 
# display body in json format explicitly with expected indent. Actually most of the time it is not very necessary because body is formatted in pretty print way.    
def pretty_print_response_json(response):
    log_api.info('{}\n{}\n\n{}\n\n{}\n'.format(
        '<-----------Response-----------',
        'Status code:' + str(response.status_code),
        '\n'.join('{}: {}'.format(k, v) for k, v in response.headers.items()),
        json.dumps(response.json(),indent=4)
        ))

class TestAPI:
    """
    Performance Test Restful HTTP API examples. 
    """ 
    def __init__(self):
        log.debug('To load test data.')  
        self.lock = asyncio.Lock()
        self.queue_tpr = asyncio.Queue()
        
        # request per seconds
        # self.rps_min = 0
        self.rps_mean = 0
        # self.rps_max = 0
        self.total_requests = 0 
        self.total_time = 0 
        
        # time per request
        self.tpr_min = 0
        self.tpr_mean = 0
        self.tpr_max = 0
        
        # failures
        self.total_failed_requests = 0      
        
        
    
    # post with headers, json body
    def test_post_headers_body_json(self):
        payload = {'key1': 1, 'key2': 'value2'}
        # No need to specify common headers as it is taken cared of by common self.post() function.
        # headers = {'Content-Type': 'application/json' } 
        
        # convert dict to json by json.dumps() for body data. It is risky to use str(payload) to convert because json format must use double quotes ("")
        url = 'http://httpbin.org/post'
        resp = self.post(url, data = json.dumps(payload,indent=4))      
        assert resp != None
        log.info('Test %s passed.' % inspect.stack()[0][3])
        """ Request HTTP body:
        {   "key1": 1, 
            "key2": "value2"
        }
        """   
        
    # get with authentication
    def test_get_auth_httpbin(self):        
        log.info('Calling %s.' % inspect.stack()[0][3])       
        username = 'user1'
        password = 'password1'
        
        url = f'http://httpbin.org/basic-auth/{username}/{password}'        
        resp =  self.get(url, auth = (username,password))
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
    # start mock service first: python flask_mock_service.py
    # Then run the tests.
    def test_mock_service(self):    
        log.info('Calling %s.' % inspect.stack()[0][3])               
        url = f'http://127.0.0.1:5000/json'        
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
        
    def post(self,url,data,headers={},verify=False,amend_headers=True):
        """
        common request post function with below features, which you only need to take care of url and body data:
            - append common headers
            - print request and response in API log file
            - Take care of request exception and non-200 response codes and return None, so you only need to care normal json response.
            - arguments are the same as requests.post, except amend_headers.
        
        verify: False - Disable SSL certificate verification 
        """
        
        # append common headers if none
        headers_new = headers
        if amend_headers == True:
            # headers = {'Content-Type':r'application/json', User-Agent:'Python Requests'}
            if not headers_new.__contains__('Content-Type'):
                headers_new['Content-Type']=r'application/json'
            if not headers_new.__contains__('User-Agent'):
                headers_new['User-Agent']='Python Requests'
                
        # send post request
        resp = requests.post(url, data = data, headers = headers_new, verify = verify)
        
        # pretty request and response into API log file
        # Note: request print is common instead of checking if it is JSON body. So pass pretty formatted json string as argument to the request for pretty logging. 
        pretty_print_request(resp.request)    
        pretty_print_response_json(resp)
        log_api.info('response time in seconds: ' + str(resp.elapsed.total_seconds()) + '\n')
        
        # This return caller function's name, not this function post.
        caller_func_name = inspect.stack()[1][3]        
        if resp.status_code != 200:
            log.error('%s failed with response code %s.' %(caller_func_name,resp.status_code))
            return None
        return resp.json()

    def get(self,url,auth = None,verify=False):
        """
        common request get function with below features, which you only need to take care of url:
            - print request and response in API log file
            - Take care of request exception and non-200 response codes and return None, so you only need to care normal json response.
            - arguments are the same as requests.get
        
        verify: False - Disable SSL certificate verification 
        """
        try:
            if auth == None:
                resp = requests.get(url, verify = verify)
            else:
                resp = requests.get(url, auth = auth, verify = verify)
        except Exception as ex:
            log.err('requests.get() failed with exception:', str(ex))
            return None
        
        # pretty request and response into API log file
        pretty_print_request(resp.request)    
        pretty_print_response_json(resp)
        log_api.info('response time in seconds: ' + str(resp.elapsed.total_seconds()) + '\n' )
        
        # This return caller function's name, not this function post.
        caller_func_name = inspect.stack()[1][3]        
        if resp.status_code != 200:
            log.error('%s failed with response code %s.' %(caller_func_name,resp.status_code))
            return None
        return resp.json()

def main():
    no_concurrent_tasks = 2
    perf_test = TestAPI()
    tasks = []
    for i in range(no_concurrent_tasks):
        task = asyncio.create_task(perf_test.test_mock_service())
        tasks.append(task)    
    await asyncio.gather(*tasks)
    print('Done.')


if __name__ == '__main__':
    asyncio.run(main())