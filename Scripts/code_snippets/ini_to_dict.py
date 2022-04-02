def ini_to_dict(input):
    """Covert a ini file to a simple dict
    """
    with open(input) as f:
        content = f.read()
    ret_dict = {}
    for line in content.split("\n"):
        if " = " in line:
            key, value = line.split(" = ", maxsplit=1)
            ret_dict[key] = value
    return ret_dict