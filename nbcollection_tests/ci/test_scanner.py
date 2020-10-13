import pytest

from nbcollection_tests.ci.tools import multi_level_ignore_repo

def test__load_ignore_data(multi_level_ignore_repo):
    from nbcollection.ci.scanner.utils import IgnoreData, load_ignore_data, \
            DEFAULT_IGNORE_ENTRIES
    ignore_data = load_ignore_data(multi_level_ignore_repo)
    for entry in ignore_data.entries:
        assert \
                entry in DEFAULT_IGNORE_ENTRIES or \
                entry in ['zero-level', 'first-level']

    assert ignore_data.__class__ is IgnoreData
    assert len(ignore_data.entries) == 8

def test__find_categories():
    pass
