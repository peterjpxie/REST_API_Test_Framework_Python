"""
Description:
Restful API testing framework example
    
Install:
pip install -r requirements.txt

Run:
pytest

Python version: 3.6 or above

Project structure:
├── inputs
├── Logs
└── Scripts

"""
from time import sleep
from datetime import datetime
import logging
from logging.handlers import RotatingFileHandler
from urllib import request
import requests
import json
import os
from os import path
import inspect
import sys
from dotmap import DotMap
import re
import pytest

### Settings ###
LOG_LEVEL = logging.DEBUG  # DEBUG, INFO, WARNING, ERROR, CRITICAL
VALID_HTTP_RESP = (200, 201, 202)


if sys.version_info < (3, 6):
    raise SystemError("Requires Python 3.6 or above.")

# root_path is parent folder of Scripts folder (one level up)
root_path = path.dirname(path.dirname(path.realpath(__file__)))

# %(levelname)7s to align 7 bytes to right, %(levelname)-7s to left.
common_formatter = logging.Formatter(
    "%(asctime)s [%(levelname)-7s][ln-%(lineno)-3d]: %(message)s",
    datefmt="%Y-%m-%d %I:%M:%S",
)

# Note: To create multiple log files, must use different logger name.
def setup_logger(log_file, level=logging.INFO, name="", formatter=common_formatter):
    """Function setup as many loggers as you want."""
    handler = logging.FileHandler(log_file, mode="w")  # default mode is append
    # Or use a rotating file handler
    # handler = RotatingFileHandler(log_file,maxBytes=1024, backupCount=5)
    handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    return logger


# default debug logger
debug_log_filename = path.join(root_path, "Logs", "debug.log")
log = setup_logger(debug_log_filename, LOG_LEVEL, "log")

# logger for API outputs
api_formatter = logging.Formatter(
    "%(asctime)s: %(message)s", datefmt="%Y-%m-%d %I:%M:%S"
)
api_outputs_filename = path.join(root_path, "Logs", "api_outputs.log")
log_api = setup_logger(
    api_outputs_filename, LOG_LEVEL, "log_api", formatter=api_formatter
)

# pretty print Restful request to API log
# argument is request object
def pretty_print_request(request):
    """
    Pay attention at the formatting used in this function because it is programmed to be pretty printed and may differ from the actual request.
    """
    log_api.info(
        "{}\n{}\n\n{}\n\n{}\n".format(
            "-----------Request----------->",
            request.method + " " + request.url,
            "\n".join("{}: {}".format(k, v) for k, v in request.headers.items()),
            request.body,
        )
    )


# pretty print Restful response to API log
# argument is response object
def pretty_print_response(response):
    log_api.info(
        "{}\n{}\n\n{}\n\n{}\n".format(
            "<-----------Response-----------",
            "Status code:" + str(response.status_code),
            "\n".join("{}: {}".format(k, v) for k, v in response.headers.items()),
            response.text,
        )
    )


def pretty_print_request_json(request):
    log_api.info(
        "{}\n{}\n\n{}\n\n{}\n".format(
            "-----------Request----------->",
            request.method + " " + request.url,
            "\n".join("{}: {}".format(k, v) for k, v in request.headers.items()),
            json.dumps(json.loads(request.body), indent=4),
        )
    )


# argument is response object
# display body in json format explicitly with expected indent. Actually most of the time it is not very necessary
# because body is formatted in pretty print way.
def pretty_print_response_json(response):
    """pretty print response in json format.
    If failing to parse body in json format, print in text.
    """
    try:
        resp_data = response.json()
        resp_body = json.dumps(resp_data, indent=4)
    # if .json() fails, ValueError is raised, take text format
    except ValueError:
        resp_body = response.text

    log_api.info(
        "{}\n{}\n\n{}\n\n{}\n".format(
            "<-----------Response-----------",
            "Status code:" + str(response.status_code),
            "\n".join("{}: {}".format(k, v) for k, v in response.headers.items()),
            resp_body,
        )
    )


def dict_to_ini(dict_var, file=None):
    """Covert a dict to ini file format

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

    Example Output (return/file)
    --------------
    age = 30
    name.firstname = Peter
    name.secondname = Xie
    scores[0] = 100
    scores[1] = 99

    Note: The output is sorted.
    """
    ini_content_list = []

    def iterate_dict(var, prefix=None):
        """ """
        # recursive if dict
        if isinstance(var, dict):
            for k, v in var.items():
                if prefix is None:
                    new_prefix = k  # e.g. age
                else:
                    new_prefix = prefix + "." + k  # e.g. name.firstname
                iterate_dict(v, new_prefix)
        elif isinstance(var, list):
            for index, value in enumerate(var):
                assert (
                    prefix is not None
                )  # Invalid to start from something like iterate_dict([1,2], None)
                new_prefix = "%s[%d]" % (prefix, index)  # e.g. scores[0]
                iterate_dict(value, new_prefix)
        else:
            this_item = "%s = %s" % (prefix, var)
            nonlocal ini_content_list
            ini_content_list.append(this_item)

    assert isinstance(dict_var, dict)
    iterate_dict(dict_var, None)
    ini_content_list.sort()
    ini_content = "\n".join(ini_content_list)
    if file:
        with open(file, "w") as f:
            f.write(ini_content)

    return ini_content


def ini_to_dict(input):
    """Covert a ini file to a simple dict

    Example Input (file or content string)
    -------------
    age = 30
    name.firstname = Peter
    scores[0] = 100

    Example Output dict
    --------------
    {
    "age": "30",
    "name.firstname" : "Peter",
    "scores[0]" : "100"
    }
    """
    if path.isfile(input):
        with open(input) as f:
            content = f.read()
    else:
        return {}

    ret_dict = {}
    for line in content.split("\n"):
        if "=" in line:
            key, value = line.split("=")
            key, value = key.strip(), value.strip()
            ret_dict[key] = value
    return ret_dict


def diff_simple_dict(expected, actual, ignore=[], output_file=None):
    """Compare simple dict generated by ini_to_dict

    Params
    ------
    expected: expected dict
    actual: actual dict
    ignore: list of keys to ignore
    output_file: file to write the diff output to if provided

    Return: diff output string. Default empty string '' if no diff.

    """
    diff_list = []
    for key in expected and key not in ignore:
        # missing in actual
        if key not in actual:
            diff_list.append("- %s = %s \n" % (key, expected[key]))
        # diff
        elif expected[key] != actual[key]:
            diff_list.append("- %s = %s \n" % (key, expected[key]))
            diff_list.append("+ %s = %s \n" % (key, actual[key]))

    # more in actual (missing in expected)
    for key in actual and key not in ignore:
        if key not in expected:
            diff_list.append("+ %s = %s \n" % (key, actual[key]))

    diff_list.sort()
    diff = "\n".join(diff_list)
    if output_file:
        with open(output_file, "w") as f:
            f.write(diff)

    return diff


def parse_test_input(filename):
    """Parse request test input

    Args: filename in path
    Return: method, url, headers, data

    Sample Input:
    POST http://httpbin.org/post

    User-Agent: Python Requests
    Content-Type: application/json

    {
        "key1": 1,
        "key2": "value2"
    }
    """
    if not path.isfile(filename):
        log.error("parse_test_input: Invalid filename: %s" % filename)
        raise FileNotFoundError(filename)

    with open(filename, "r") as f:
        content = f.read()
        # 3 parts split by empty line
        parts = re.split("\s*\n\s*\n", content)
        parts_len = len(parts)

        # part 1: Method and url
        assert len(parts[0].split()) == 2
        method, url = parts[0].split()
        method, url = method.strip(), url.strip()

        # part 2: headers
        if parts_len > 1 and parts[1].strip() != "":
            header_lines = re.split("\s*\n", parts[1])
            header_lines = [line.strip() for line in header_lines]  # strip line spaces
            # print(header_lines)
            headers = dict([re.split(":\s*", line) for line in header_lines])
            # print(headers)
        else:
            headers = None

        # part 3: body
        if parts_len > 2 and parts[2].strip() != "":
            body = parts[2].strip().strip("\n")
            # print(body)
        else:
            body = None

    return method, url, headers, body


class TestAPI:
    """
    Test Restful HTTP API examples.
    """
    def setup_class(cls):
        log.debug("To load test data.")

    def test_post_headers_body_json(self):
        """post with headers, json body"""
        payload = {"key1": 1, "key2": "value2"}
        # No need to specify common headers as it is taken cared of by common self.post() function.
        # headers = {'Content-Type': 'application/json' }

        # convert dict to json by json.dumps() for body data.
        url = "http://httpbin.org/post"
        resp = self.post(url, data=json.dumps(payload, indent=4))
        assert resp != None
        # self.post converts the return to json if it is not None
        assert resp["url"] == url
        assert resp["json"]["key1"] == 1
        # dot fashion with DotMap
        assert DotMap(resp).json.key1 == 1
        log.info("Test %s passed." % inspect.stack()[0][3])
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

    def test_post_normal_body(self):
        """post with headers, json body"""
        payload = {"key1": 1, "key2": "value2"}
        url = "http://httpbin.org/post"
        resp = self.post(url, data=payload, amend_headers=False)
        assert resp != None
        log.info("Test %s passed." % inspect.stack()[0][3])
        """ Request HTTP body:
        key1=1&key2=value2
        """

    def test_get_auth_httpbin(self):
        """get with authentication"""
        log.info("Calling %s." % inspect.stack()[0][3])
        username = "user1"
        password = "password1"

        url = f"http://httpbin.org/basic-auth/{username}/{password}"
        resp = self.get(url, auth=(username, password))
        assert resp != None
        assert resp["authenticated"] == True
        log.info("Test %s passed." % inspect.stack()[0][3])
        """ json response
        {
        "authenticated": true, 
        "user": "user1"
        }
        """

    def test_mock_service(self):
        """test with mock service

        Start mock service first: python flask_mock_service.py
        """
        log.info("Calling %s." % inspect.stack()[0][3])
        url = "http://127.0.0.1:5000/hello"
        resp = self.get(url)
        assert resp != None
        assert resp["code"] == 1
        log.info("Test %s passed." % inspect.stack()[0][3])
        """ json response
        {
        "code": 1,
        "message": "Hello, World!"
        }
        """

    def test_mock_service_dynamic(self):
        """test with dynamic mocking where expected response status code and body data are set in the request headers"""
        log.info("Calling %s." % inspect.stack()[0][3])
        url = "http://127.0.0.1:5000/anyendpoint"
        response_code = "202"
        response_body = '{"code": 0, "message": "all good"}'
        headers = {"response_code": response_code, "response_body": response_body}
        resp = self.get(url, headers=headers)
        assert resp != None
        assert resp["code"] == 0
        log.info("Test %s passed." % inspect.stack()[0][3])
        """ response
        202 
        
        {"code": 0, "message": "all good"}
        """


    @pytest.mark.parametrize("testcase_folder", ["test_case_01", "test_case_02"])
    def test_by_input_output_text(self, testcase_folder):
        """test by input and expected output text files

        Write only this test function and use parametrize method to test different cases by:
        - read input request text files
        - compare output with expected output text files where json content is converted to ini format for easy comparison

        Best Practice:
        For the first run, no need to prepare the expected output files. 
        Run it without expect files, examine the output manually, then copy output folder as expect folder if passed.
        """
        # post
        input_root = path.join(root_path,"inputs")
        output_root = path.join(root_path,"outputs")
        expect_root = path.join(root_path,"expects")
        diff_root = path.join(root_path,"diff")
        testcase_full_dir = path.join(input_root, testcase_folder)
        for request_file in os.listdir(testcase_full_dir):
            # parse input files
            request_file_path = path.join(testcase_full_dir, request_file)
            log.info("Test by input file %s" % request_file_path)
            method, url, headers, body = parse_test_input(request_file_path)
            log.debug("Parsed request:")
            log.debug("%s %s\n%s\n%s" % (method, url, headers, body))

            resp = self.request(method, url, headers, body)

            assert resp != None
            # write response dict to ini output
            output_file_dir = path.join(output_root, testcase_folder)
            os.makedirs(output_file_dir)
            output_filename = request_file.replace("request", "response")
            output_file_path = path.join(output_file_dir, output_filename)
            # convert to a ini file
            dict_to_ini(resp, output_file_path)
            expect_file_dir = path.join(expect_root, testcase_folder)
            os.makedirs(expect_file_dir)
            expect_file_path = path.join(expect_file_dir, output_filename)
            # todo - compare
            actual = ini_to_dict(output_file_path)
            expected = ini_to_dict(expect_file_path)
            diff_file_dir = path.join(diff_root, testcase_folder)
            os.makedirs(diff_file_dir)
            diff_file_path = path.join(diff_file_dir, output_filename)
            diff = diff_simple_dict(actual, expected, ignore=[], output_file=diff_file_path)
            assert diff == []
            log.info("Test %s passed." % inspect.stack()[0][3])

    def post(self, url, data, headers={}, amend_headers=True, verify=False):
        """
        Common request post function with below features, which you only need to take care of url and body data:
            - append common headers (when amend_headers=True)
            - print request and response in API log file
            - Take care of request exception and non-20x response codes and return None, so you only need to care normal json response.
            - arguments are the same as requests.post, except amend_headers.

        verify: False - Disable SSL certificate verification

        Return: response dict or None
        """

        # append common headers if none
        headers_new = headers
        if amend_headers == True:
            headers_new["Content-Type"] = r"application/json"
            headers_new["User-Agent"] = "Python Requests"

        # send post request
        try:
            resp = requests.post(url, data=data, headers=headers_new, verify=verify)
        except Exception as ex:
            log.error("requests.post() failed with exception: %s" % str(ex))
            return None

        # pretty request and response into API log file
        # Note: request print is common instead of checking if it is JSON body. So pass pretty formatted json string as argument to the request for pretty logging.
        pretty_print_request(resp.request)
        pretty_print_response_json(resp)

        # This returns caller function's name, not this function post.
        caller_func_name = inspect.stack()[1][3]
        if resp.status_code not in VALID_HTTP_RESP:
            log.error(
                "%s failed with response code %s."
                % (caller_func_name, resp.status_code)
            )
            return None
        return resp.json()

    def get(self, url, headers={}, auth=None, verify=False):
        """
        Common request get function with below features, which you only need to take care of url:
            - print request and response in API log file
            - Take care of request exception and non-20x response codes and return None, so you only need to care normal json response.
            - arguments are the same as requests.get

        verify: False - Disable SSL certificate verification

        Return: response dict or None
        """
        try:
            resp = requests.get(url, headers=headers, auth=auth, verify=verify)
        except Exception as ex:
            log.error("requests.get() failed with exception: %s" % str(ex))
            return None

        # pretty request and response into API log file
        pretty_print_request(resp.request)
        pretty_print_response_json(resp)

        # This return caller function's name, not this function post.
        caller_func_name = inspect.stack()[1][3]
        if resp.status_code not in VALID_HTTP_RESP:
            log.error(
                "%s failed with response code %s."
                % (caller_func_name, resp.status_code)
            )
            return None
        return resp.json()

    def request(
        self,
        method,
        url,
        headers={},
        data=None,
        amend_headers=True,
        verify=False,
        **kwargs,
    ):
        """
        Common request function with below features, which can be used for any request methods such as post, get, delete, put etc.:
            - append common headers (when amend_headers=True)
            - print request and response in API log file
            - Take care of request exception and non-20x response codes and return None, so you only need to care normal json response.
            - arguments are the same as requests.request, except amend_headers.

        Arguments
        ---------
        amend_headers: Append common headers, e.g. Content-Type
        verify:        False - Disable SSL certificate verification
        kwargs:        Other arguments requests.request takes.

        Return: response dict or None
        """

        # append common headers if none
        headers_new = headers
        if amend_headers == True:
            headers_new["Content-Type"] = r"application/json"
            headers_new["User-Agent"] = "Python Requests"

        # send request
        try:
            resp = requests.request(
                method, url, headers=headers_new, data=data, verify=verify, **kwargs
            )
        except Exception as ex:
            log.error("requests.request() failed with exception: %s" % str(ex))
            return None

        # pretty request and response into API log file
        # Note: request print is common instead of checking if it is JSON body. So pass pretty formatted json string as argument to the request for pretty logging.
        pretty_print_request(resp.request)
        pretty_print_response_json(resp)

        # This returns caller function's name, not this function post.
        caller_func_name = inspect.stack()[1][3]
        if resp.status_code not in VALID_HTTP_RESP:
            log.error(
                "%s failed with response code %s."
                % (caller_func_name, resp.status_code)
            )
            return None
        return resp.json()


if __name__ == "__main__":
    # self test
    # post
    method, url, headers, body = parse_test_input(
        "../inputs/test_case_01/request_01.txt"
    )
    print("\n".join([method, url, str(headers), body]))
    tests = TestAPI()
    resp = tests.request(method, url, headers, body)
    print(json.dumps(resp, indent=4))
    # get
    method, url, headers, body = parse_test_input(
        "../inputs/test_case_02/request_01.txt"
    )
    print("\n".join([method, url, str(headers), str(body)]))
    # tests = TestAPI()
    resp = tests.request(method, url, headers, body)
    print(json.dumps(resp, indent=4))

    pass
