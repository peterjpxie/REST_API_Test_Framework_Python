#!/bin/bash

grep "def test" test*.py /dev/null
# Note 'pytest --collect-only' is slow
# pytest --collect-only |grep "Function test"
