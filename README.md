# A RESTful API Test Framework Example
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
## Features:
* Support both functional and performance tests
* Test by parametrized input / output text files
* Use flask to mock API services dynamically with magic
* HTML report
* Common get/post/request functions to:
    1. Print every request and response in an API output file
    2. Append common headers
    3. Handle request exceptions and non-20X response codes, so you only need to focus on normal json response.
    
## Install:
`pip install -r Scripts/requirements.txt`

## Run:
`cd Scripts`

**Start API mock services:**

`python flask_mock_service.py`

**Run Functional tests:**

`pytest`

**Run Performance tests:**

`python perf_test_rest_api.py`

## Medium Post
Check out the [medium post](https://medium.com/@peter.jp.xie/rest-api-testing-using-python-751022c364b8?source=friends_link&sk=bb13119f8c0e8e6d5b071eca8c22e29c) for more details.

## HTML Report
For HTML report generation, we are using [pytest-html](https://pypi.org/project/pytest-html/) which is simple and effective.

Other alternatives to generate **fancier** HTML reports are [Allure](https://github.com/allure-framework) and [reportportal](https://reportportal.io/installation). Note these report frameworks are heavy, espcially reportportal.
