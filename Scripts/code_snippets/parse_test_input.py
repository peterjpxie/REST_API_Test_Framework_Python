def parse_test_input(filename):
    """Parse request test input
    """
    import re
    with open(filename, "r") as f:
        content = f.read()
        # 3 parts split by empty line
        parts = re.split("\n\n", content)
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