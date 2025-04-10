#!/usr/bin/env python3
import os

cmd = 'egrep "def test|class Test" test*.py /dev/null'
print(f"+ {cmd}")
os.system(cmd)
# Note 'pytest --collect-only' is slow
# pytest --collect-only |grep "Function test"