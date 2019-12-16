import logging
import os
import shutil

from nbconvert.preprocessors.execute import CellExecutionError
import pytest

from nbstatic.core import NBStaticNotebook, BUILD_DIR_NAME
from nbstatic.logger import logger


def get_test_cases(case_i=None):
    test_root_path = os.path.dirname(__file__)

    cases = []

    # /path/to/the/notebook1.ipynb
    # -> /path/to/the/_build/exec_notebook1.ipynb
    # -> /path/to/the/_build/notebook1.html
    nb_name = 'notebook1'
    nb_path = os.path.join(test_root_path, 'data', 'nb_test1',
                           f'{nb_name}.ipynb')
    build_path = os.path.join(test_root_path, 'data', 'nb_test1',
                              BUILD_DIR_NAME)
    cases.append((nb_name, nb_path, build_path, ''))

    # Flat, multiple notebooks:
    # /path/to/the/ containing: notebook1.ipynb, notebook2.ipynb
    # -> /path/to/the/_build/exec_notebook1.ipynb
    # -> /path/to/the/_build/notebook1.html
    # -> /path/to/the/_build/exec_notebook2.ipynb
    # -> /path/to/the/_build/notebook2.html
    for i in [1, 2]:
        nb_name = f'notebook{i}'
        nb_path = os.path.join(test_root_path, 'data', 'nb_test2',
                               f'{nb_name}.ipynb')
        build_path = os.path.join(test_root_path, 'data', 'nb_test2',
                                  BUILD_DIR_NAME)
        cases.append((nb_name, nb_path, build_path, ''))

    # Nested, multiple notebooks:
    # /path/to/the/ containing: nb1/notebook1.ipynb, nb2/notebook2.ipynb
    # -> /path/to/the/_build/nb1/exec_notebook1.ipynb
    # -> /path/to/the/_build/nb1/notebook1.html
    # -> /path/to/the/_build/nb2/exec_notebook2.ipynb
    # -> /path/to/the/_build/nb2/notebook2.html
    for i in [1, 2]:
        nb_name = f'notebook{i}'
        nb_path = os.path.join(test_root_path, 'data', 'nb_test3', f'nb{i}',
                               f'{nb_name}.ipynb')
        build_path = os.path.join(test_root_path, 'data', 'nb_test3',
                                  BUILD_DIR_NAME)
        cases.append((nb_name, nb_path, build_path, f'nb{i}'))

    # notebook: /path/to/the/notebook1.ipynb
    # build: /tmp
    # -> /tmp/exec_notebook1.ipynb
    # -> /tmp/notebook1.html
    nb_name = 'notebook1'
    nb_path = os.path.join(test_root_path, 'data', 'nb_test1',
                           f'{nb_name}.ipynb')
    cases.append((nb_name, nb_path, None, ''))

    for i in [1, 2]:
        nb_name = f'notebook{i}'
        nb_path = os.path.join(test_root_path, 'data', 'nb_test2',
                               f'{nb_name}.ipynb')
        cases.append((nb_name, nb_path, None, ''))

    if case_i is None:
        return len(cases)
    else:
        return cases[case_i]


@pytest.mark.parametrize('case_i', range(get_test_cases()))
def test_nbstaticnotebook(tmpdir, caplog, case_i):
    logger.setLevel(logging.DEBUG)

    nb_name, nb_path, build_path, post_build = get_test_cases(case_i)

    if build_path is None:
        build_path = str(tmpdir)

    # if os.path.exists(build_path):
    #     shutil.rmtree(build_path)

    nb = NBStaticNotebook(nb_path, build_path)

    # First, just check that the paths are what we expect:
    assert nb.nb_exec_path == os.path.abspath(os.path.join(
        build_path, post_build, f'exec_{nb_name}.ipynb'))
    assert nb.nb_html_path == os.path.abspath(os.path.join(
        build_path, post_build, f'{nb_name}.html'))

    # Now try executing:
    nb.execute(kernel_name='python3')
    assert 'Use overwrite=True' not in caplog.records[-1].message
    nb.execute(kernel_name='python3')
    assert 'Use overwrite=True' in caplog.records[-1].message

    nb.execute(kernel_name='python3', overwrite=True)
    assert 'Use overwrite=True' not in caplog.records[-1].message

    # Convert to HTML:
    nb.convert()


def test_convert_pass(tmpdir):
    # With the current master version of nbconvert, we can allow errors
    # per-cell. This notebook, even though it raises an exception, should still
    # execute fine:
    test_root_path = os.path.dirname(__file__)
    nb_path = os.path.join(test_root_path, 'data',
                           'exception-should-pass.ipynb')
    build_path = str(tmpdir)

    nb = NBStaticNotebook(nb_path, build_path)
    nb.execute(kernel_name='python3')


def test_convert_fail(tmpdir):
    # This notebook raises an exception in a cell, but doesn't use the
    # 'raises-exception' tag in the cell metadata, so it should fail
    test_root_path = os.path.dirname(__file__)
    nb_path = os.path.join(test_root_path, 'data',
                           'exception-should-fail.ipynb')
    build_path = str(tmpdir)

    nb = NBStaticNotebook(nb_path, build_path)
    with pytest.raises(CellExecutionError):
        nb.execute(kernel_name='python3')


def teardown_module():
    for case in range(get_test_cases()):
        *_, build_path, _ = get_test_cases(case)

        if build_path is not None and os.path.exists(build_path):
            shutil.rmtree(build_path)
