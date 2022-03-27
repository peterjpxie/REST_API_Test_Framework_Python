@pytest.mark.parametrize("testcase_folder", test_case_list)
def test_by_input_output_text(self, testcase_folder):
    """test by input and expected output text files

    Write only this test function and use parametrize method to test different cases by:
    - read input request text files
    - compare output with expected output text files where json content is converted to ini format for easy comparison

    Best Practice:
    For the first run, no need to prepare the expected output files.
    Run it without expect files, examine the output manually, then copy output folder as expect folder if passed.
    """
    # post
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
        log.info("Test by input file %s" % request_file_path)
        method, url, headers, body = parse_test_input(request_file_path)
        log.debug("Parsed request:")
        log.debug("%s %s\n%s\n%s" % (method, url, headers, body))

        resp = self.request(method, url, headers, body)

        assert resp != None
        # write response dict to ini output
        output_file_dir = path.join(output_root, testcase_folder)
        os.makedirs(output_file_dir, exist_ok=True)
        output_filename = request_file.replace("request_", "response_")
        output_file_path = path.join(output_file_dir, output_filename)
        # convert to a ini file
        dict_to_ini(resp, output_file_path)
        expect_file_dir = path.join(expect_root, testcase_folder)
        expect_file_path = path.join(expect_file_dir, output_filename)
        # compare
        actual = ini_to_dict(output_file_path)
        expected = ini_to_dict(expect_file_path)
        ignore_filename = request_file.replace(".txt", ".ignore")
        ignore_file_path = path.join(testcase_full_dir, ignore_filename)
        ignore = parse_ignore_file(ignore_file_path)

        diff_file_dir = path.join(diff_root, testcase_folder)
        os.makedirs(diff_file_dir, exist_ok=True)
        diff_file_path = path.join(diff_file_dir, output_filename)
        diff = diff_simple_dict(
            actual, expected, ignore=ignore, output_file=diff_file_path
        )
        assert diff == "", "response does not match expected output"
        log.info("Test %s[%s] passed." % (inspect.stack()[0][3], testcase_folder))