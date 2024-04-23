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
├── outputs
├── expects
├── diff
├── Logs
└── Scripts
"""
import copy
import logging
import requests
import json
import os
from os import path
import inspect
import sys
from dotmap import DotMap
import re
import pytest
import shutil
import pdb

### Settings ###
LOG_LEVEL = logging.INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL

if sys.version_info < (3, 8):
    raise SystemError("Requires Python 3.8 or above.")

# root_path is parent folder of Scripts folder (one level up)
root_path = path.dirname(path.dirname(path.realpath(__file__)))

# %(levelname)7s to align 7 bytes to right, %(levelname)-7s to left.
common_formatter = logging.Formatter(
    "%(asctime)s [%(levelname)-7s][%(lineno)-3d]: %(message)s",
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
os.makedirs(path.join(root_path, "Logs"), exist_ok=True)
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

### Setup ###
# get input test case lists for parametrized tests
test_case_list = []
input_root = path.join(root_path, "inputs")
if path.isdir(input_root):
    for tc in os.listdir(input_root):
        if tc.startswith("test_case"):
            test_case_list.append(tc)
test_case_list.sort()

# clear up old diff and output files
diff_root = path.join(root_path, "diff")
output_root = path.join(root_path, "outputs")
shutil.rmtree(diff_root, ignore_errors=True)
shutil.rmtree(output_root, ignore_errors=True)


def pretty_print_request(request):
    """pretty print request

    Params
    ------
    request:   requests' request object
    """
    log_api.info(
        "{}\n{}\n\n{}\n\n{}\n".format(
            "-----------Request----------->",
            request.method + " " + request.url,
            "\n".join("{}: {}".format(k, v) for k, v in request.headers.items()),
            request.body,
        )
    )


def pretty_print_request_json(request):
    """pretty print request in json format
    Note it may differ from the actual request as it is pretty formatted.

    Params
    ------
    request:   requests' request object
    """
    log_api.info(
        "{}\n{}\n\n{}\n\n{}\n".format(
            "-----------Request----------->",
            request.method + " " + request.url,
            "\n".join("{}: {}".format(k, v) for k, v in request.headers.items()),
            json.dumps(json.loads(request.body), indent=4),
        )
    )


def pretty_print_response_json(response):
    """pretty print response in json format
    If failing to parse body in json format, print in text.

    Params
    ------
    response:   requests' response object
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
        """iterate dict and convert to a list of 'key1.key2[i] = value' string"""
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
            # for multiple line string, i.e. with \n, convert to 1 line repr string
            if isinstance(var, str) and "\n" in var:
                var = repr(var)
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
        if " = " in line:
            key, value = line.split(" = ", maxsplit=1)
            key, value = key.strip(), value.strip()
            ret_dict[key] = value
    return ret_dict


def parse_ignore_file(file):
    """Parse ignore file and return a list of ignored keys"""
    ignore_keys = []
    if path.isfile(file):
        with open(file) as f:
            for line in f:
                if line.strip != "":
                    ignore_keys.append(line.strip())

    return ignore_keys


def diff_simple_dict(expected, actual, ignore=[], output_file=None):
    """Compare simple dict generated by ini_to_dict

    Params
    ------
    expected:   expected dict
    actual:     actual dict
    ignore:     list of keys to ignore
    output_file: file to write the diff output to if provided

    Return: diff output string. Default empty string '' if no diff.
    """
    diff_list = []
    for key in expected:
        if key not in ignore:
            # missing in actual
            if key not in actual:
                diff_list.append("- %s = %s" % (key, expected[key]))
            # diff
            elif expected[key] != actual[key]:
                diff_list.append("- %s = %s" % (key, expected[key]))
                diff_list.append("+ %s = %s" % (key, actual[key]))

    # more in actual (missing in expected)
    for key in actual:
        if key not in ignore:
            if key not in expected:
                diff_list.append("+ %s = %s" % (key, actual[key]))

    diff = "\n".join(diff_list)
    if output_file and diff != "":
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
            headers = dict([re.split(":\s*", line) for line in header_lines])
        else:
            headers = {}

        # part 3: body
        if parts_len > 2 and parts[2].strip() != "":
            body = parts[2].strip().strip("\n")
        else:
            body = None

    return method, url, headers, body


class TestAPI:
    """
    Test Restful API examples.
    """

    def test_post_headers_body_json(self):
        """post with headers, json body"""
        payload = {"key1": 1, "key2": "value2"}
        # No need to specify common headers as it is taken cared of by common self.post() function.
        # headers = {'Content-Type': 'application/json' }
        headers = {"User-Agent": "Python Requests"}

        # convert dict to json by json.dumps() for body data.
        url = "http://httpbin.org/post"
        resp = self.post(url, headers=headers, data=json.dumps(payload, indent=4))
        assert resp != None
        # self.post converts the return to json if it is not None
        assert resp["url"] == url
        assert resp["json"]["key1"] == 1
        # dot fashion with DotMap
        assert DotMap(resp).json.key1 == 1
        this_function_name = inspect.stack()[0].function
        log.info("Test %s passed." % this_function_name)
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
            "User-Agent": "Python Requests"
        },
        "json": {
            "key1": 1,
            "key2": "value2"
        },
        "origin": "103.115.210.48, 103.115.210.48",
        "url": "https://httpbin.org/post"
        }
        """

    def test_post_query_string_body(self):
        """post with query string body"""
        payload = {"key1": 1, "key2": "value2"}
        url = "http://httpbin.org/post"
        resp = self.post(url, data=payload, amend_headers=False)
        assert resp != None
        log.info("Test %s passed." % inspect.stack()[0].function)
        """ Request HTTP body:
        key1=1&key2=value2
        """

    def test_get_auth_httpbin(self):
        """get with authentication"""
        log.info("Calling %s." % inspect.stack()[0].function)
        username = "user1"
        password = "password1"

        url = f"http://httpbin.org/basic-auth/{username}/{password}"
        resp = self.get(url, auth=(username, password))
        assert resp != None
        assert resp["authenticated"] == True
        log.info("Test %s passed." % inspect.stack()[0].function)
        """ json response
        {
        "authenticated": true, 
        "user": "user1"
        }
        """

    def test_mock_service_simple(self):
        """test with mock service

        Start mock service first: python flask_mock_service.py
        """
        log.info("Calling %s." % inspect.stack()[0].function)
        url = "http://127.0.0.1:5000/hello"
        # url = "http://127.0.0.1:5000/hello/binary"
        resp = self.get(url)
        assert resp != None
        # assert resp["code"] == 1
        log.info("Test %s passed." % inspect.stack()[0].function)
        """ json response
        {
        "code": 1,
        "message": "Hello, World!"
        }
        """

    def test_mock_service_dynamic(self):
        """test with dynamic mocking where expected response status code and body data are set in the request headers"""
        log.info("Calling %s." % inspect.stack()[0].function)
        url = "http://127.0.0.1:5000/anyendpoint"
        response_code = "202"
        response_body = '{"code": 0, "message": "all good"}'
        headers = {"Response-Code": response_code, "Response-Body": response_body}
        resp = self.get(url, headers=headers)
        assert resp != None
        assert resp["code"] == 0
        log.info("Test %s passed." % inspect.stack()[0].function)
        """ response
        202 
        
        {"code": 0, "message": "all good"}
        """

    @pytest.mark.parametrize("testcase_folder", test_case_list)
    def test_by_input_output_text(self, testcase_folder):
        """test by input and expected output text files

        Write only this test function and use parametrize method to test different cases by:
        - read input request text files
        - compare output with expected output text files where json content is converted to ini format for easy comparison

        Best Practice:
        For the first run, no need to prepare the expected output files.
        Run it without expect files, examine the output manually, then copy output folder as expect folder if passed.
        """
        input_root = path.join(root_path, "inputs")
        output_root = path.join(root_path, "outputs")
        expect_root = path.join(root_path, "expects")
        diff_root = path.join(root_path, "diff")
        testcase_full_dir = path.join(input_root, testcase_folder)
        # get and sort all request files
        request_files = []
        for request_file in os.listdir(testcase_full_dir):
            if request_file.endswith(".txt"):
                # ignore non-request text files, i.e. .ignore files
                request_files.append(request_file)
        request_files.sort()

        for request_file in request_files:
            # parse input files
            request_file_path = path.join(testcase_full_dir, request_file)
            log.info("Test by input file %s" % request_file_path)
            method, url, headers, body = parse_test_input(request_file_path)
            log.debug("Parsed request:")
            log.debug("%s %s\n%s\n%s" % (method, url, headers, body))

            resp = self.request(method, url, headers, body)
            assert resp != None

            # write response dict to a ini format file
            output_file_dir = path.join(output_root, testcase_folder)
            os.makedirs(output_file_dir, exist_ok=True)
            output_filename = request_file.replace("request_", "response_")
            output_file_path = path.join(output_file_dir, output_filename)
            dict_to_ini(resp, output_file_path)

            # compare
            expect_file_dir = path.join(expect_root, testcase_folder)
            expect_file_path = path.join(expect_file_dir, output_filename)
            ignore_filename = request_file.replace(".txt", ".ignore")
            ignore_file_path = path.join(testcase_full_dir, ignore_filename)
            diff_file_dir = path.join(diff_root, testcase_folder)
            os.makedirs(diff_file_dir, exist_ok=True)
            diff_file_path = path.join(diff_file_dir, output_filename)

            actual = ini_to_dict(output_file_path)
            expected = ini_to_dict(expect_file_path)
            ignore = parse_ignore_file(ignore_file_path)
            diff = diff_simple_dict(
                expected, actual, ignore=ignore, output_file=diff_file_path
            )
            assert diff == "", "response does not match expected output"
            log.info(
                "Test %s[%s] passed." % (inspect.stack()[0].function, testcase_folder)
            )

    def post(
        self, url, headers={}, data=None, verify=False, amend_headers=True, **kwargs
    ):
        """
        request shorthand for POST method
        """
        return self.request("POST", url, headers, data, verify, amend_headers=amend_headers, **kwargs)

    def get(self, url, headers={}, verify=False, auth=None, **kwargs):
        """
        request shorthand for GET method
        """
        return self.request("GET", url, headers, data=None, verify=verify, auth=auth, amend_headers=False, **kwargs)

    def request(
        self,
        method,
        url,
        headers={},
        data=None,  # NA for GET
        verify=False,
        auth=None,  # NA for POST
        amend_headers=True,  # NA for GET
        **kwargs
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

        Return:     response dict (Normal REST should be this) 
                    or decoded text if not json
                    or raw content bytes if not decoded 
                    or '' if no content in response body
                    or None if error.
        """
        # append common headers
        # deep copy headers to avoid using the same headers object (default {}) in different requests
        headers_new = copy.deepcopy(headers)
        if amend_headers is True:
            # check if body is json, then set content type to json
            if data:
                try:
                    json.loads(data)
                except (json.JSONDecodeError, TypeError):
                    pass
                else:
                    headers_new["Content-Type"] = "application/json"

        # send request
        try:
            resp = requests.request(
                method, url, headers=headers_new, data=data, verify=verify, auth=auth, **kwargs
            )
        except Exception as ex:
            log.error("requests.request() failed with exception: %s" % str(ex))
            return None

        # pretty request and response into API log file
        # Note: request print is common as it could be a JSON body or a normal text
        pretty_print_request(resp.request)
        pretty_print_response_json(resp)

        # This returns caller's function name, not this function request.
        caller_func_name = inspect.stack()[1].function
        if not (resp.status_code >= 200 and resp.status_code < 300):            
            log.error(
                "%s failed with response code %s."
                % (caller_func_name, resp.status_code)
            )
            return None
        
        if resp.content:
            # return json if possible
            try:
                return resp.json()
            except requests.exceptions.JSONDecodeError:
                try:
                    # It returns string 'A\x11\x12B' for b'\x41\x11\x12\x42' - ascii binary data with unprintable characters (\x11\x12)
                    #   NB: print('A\x11\x12B') prints 'AB' in terminal as \x11\x12 are unprintable characters, but will write A^Q^RB to file. 
                    # It returns unreadable string '��' for b'\xf1\xf2' - non-decodable (>127) utf8 binary data
                    return resp.text
                except Exception:
                    # most likely won't reach here
                    return resp.content
        else: # no content in response body, i.e. content = b''.
            return ''

if __name__ == "__main__":
    # self test
    pass
