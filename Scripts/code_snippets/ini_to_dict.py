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