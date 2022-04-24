import pytest

@pytest.mark.parametrize("testcase_folder", test_case_list)
def test_by_input_output_text(testcase_folder):
    """test by input and expected output text files"""
    import os
    from os import path
    import requests
    input_root = path.join(root_path, "inputs")
    output_root = path.join(root_path, "outputs")
    expect_root = path.join(root_path, "expects")
    diff_root = path.join(root_path, "diff")
    testcase_full_dir = path.join(input_root, testcase_folder)

    for request_file in os.listdir(testcase_full_dir):
        if not request_file.endswith(".txt"):
            # ignore non-request text files, i.e. .ignore files
            continue

        # parse input files
        request_file_path = path.join(testcase_full_dir, request_file)
        method, url, headers, body = parse_test_input(request_file_path)
        
        resp = requests.request(method, url, headers=headers, data=body, verify=False)
        assert resp.status_code in (200, 201, 202)
        resp = resp.json() # convert to dict

        ## write response dict to ini output
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
        diff = diff_simple_dict(actual, expected, ignore=ignore, output_file=diff_file_path)
        assert diff == "", "response does not match expected output"