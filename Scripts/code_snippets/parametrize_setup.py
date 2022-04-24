"""get input test case lists for parametrized tests"""
import os
from os import path
# root_path is parent folder of Scripts folder
root_path = path.dirname(path.dirname(path.realpath(__file__)))
test_case_list = []
input_root = path.join(root_path, "inputs")
for tc in os.listdir(input_root):
    if tc.startswith("test_case"):
        test_case_list.append(tc)