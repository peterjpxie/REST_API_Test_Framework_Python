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
            headers = {}

        # part 3: body
        if parts_len > 2 and parts[2].strip() != "":
            body = parts[2].strip().strip("\n")
            # print(body)
        else:
            body = None

    return method, url, headers, body