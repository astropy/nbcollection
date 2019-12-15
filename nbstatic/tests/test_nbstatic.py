import os
import pytest
from nbstatic.convert import NBStaticNotebook, BUILD_DIR_NAME


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
    cases.append((nb_name, nb_path, '/tmp', ''))

    for i in [1, 2]:
        nb_name = f'notebook{i}'
        nb_path = os.path.join(test_root_path, 'data', 'nb_test2',
                               f'{nb_name}.ipynb')
        cases.append((nb_name, nb_path, '/tmp', ''))

    if case_i is None:
        return len(cases)
    else:
        return cases[case_i]


@pytest.mark.parametrize('case_i', range(get_test_cases()))
def test_nbstaticnotebook_paths(case_i):
    nb_name, nb_path, build_path, post_build = get_test_cases(case_i)

    nb = NBStaticNotebook(nb_path, build_path)
    assert nb.nb_exec_path == os.path.abspath(os.path.join(
        build_path, post_build, f'exec_{nb_name}.ipynb'))
    assert nb.nb_html_path == os.path.abspath(os.path.join(
        build_path, post_build, f'{nb_name}.html'))
