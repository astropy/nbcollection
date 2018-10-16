# Standard library
from os import path, remove

# Third-party
import pytest

# This project
from ..converter import NBPagesConverter

tests_path = path.split(path.abspath(__file__))[0]

def test_convert_succeed():
    # With the current master version of nbconvert, we can allow errors
    # per-cell. This notebook, even though it raises an exception, should still
    # execute fine:
    nbc = NBPagesConverter(path.join(tests_path, 'test-succeed.ipynb'))
    filename = nbc.execute()
    remove(filename) # clean up

def test_convert_fail():
    # This notebook raises an exception in a cell, but doesn't use the
    # 'raises-exception' tag in the cell metadata, so it should fail
    nbc = NBPagesConverter(path.join(tests_path, 'test-fail.ipynb'))

    with pytest.raises(Exception):
        nbc.execute()
