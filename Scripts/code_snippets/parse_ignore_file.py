def parse_ignore_file(file):
    """Parse ignore file and return a list of ignored keys"""
    from os import path
    ignore_keys = []
    if path.isfile(file):
        with open(file) as f:
            for line in f:
                if line.strip != "":
                    ignore_keys.append(line.strip())
    return ignore_keys