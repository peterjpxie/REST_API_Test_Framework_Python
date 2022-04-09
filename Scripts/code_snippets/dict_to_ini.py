def dict_to_ini(dict_var, file=None):
    ini_content_list = []
    def iterate_dict(var, prefix=None):
        """iterate dict and convert to a list of 'key1.key2[i] = value' string"""
        if isinstance(var, dict):
            for k, v in var.items():
                if prefix is None:
                    new_prefix = k  # e.g. age
                else:
                    new_prefix = prefix + "." + k  # e.g. name.firstname
                iterate_dict(v, new_prefix)
        elif isinstance(var, list):
            for index, value in enumerate(var):
                new_prefix = "%s[%d]" % (prefix, index)  # e.g. scores[0]
                iterate_dict(value, new_prefix)
        else:
            # for multiple line string, i.e. with \n, convert to 1 line repr string
            if isinstance(var, str) and "\n" in var:
                var = repr(var)            
            this_item = "%s = %s" % (prefix, var)
            nonlocal ini_content_list
            ini_content_list.append(this_item)

    iterate_dict(dict_var, None)
    ini_content_list.sort()
    ini_content = "\n".join(ini_content_list)
    if file:
        with open(file, "w") as f:
            f.write(ini_content)
    return ini_content