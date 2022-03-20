# A RESTful API Test Framework Example
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
## Features:
* Support both functional and performance tests

* Common get/post function to 

1. Print every request and response in a API output file
2. Append common headers
3. Take care of request exception and non-200 response codes and return None, so you only need to care normal json response.
        
* Use flask to mock API services dynamically with magic

* html report
    
## Install:

pip install -r Scripts/requirements.txt

## Run:
cd Scripts

**Start API mock services:**

python flask_mock_service.py

**Run Functional tests:**

pytest

**Run Performance tests:**

python perf_test_rest_api.py 

## Medium Post
Check out the [medium post](https://medium.com/@peter.jp.xie/rest-api-testing-using-python-751022c364b8?source=friends_link&sk=bb13119f8c0e8e6d5b071eca8c22e29c) for more details.
