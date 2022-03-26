from flask import Flask, request

app = Flask(__name__)


@app.before_request
def mock_dynamic():
    headers = request.headers
    response_code = headers.get("response_code", 200)
    response_body = headers.get("response_body")
    if response_body is None:
        return '{"message": "response_body is not set." }'
    else:
        return response_body, int(response_code)


app.run(host="127.0.0.1", port="5000", debug=True)
