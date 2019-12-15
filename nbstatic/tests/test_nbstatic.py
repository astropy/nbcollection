import os

from nbstatic.convert import NBStaticNotebook, BUILD_DIR_NAME


def test_nbstaticnotebook():
    test_root_path = os.path.dirname(__file__)

    # /path/to/the/notebook1.ipynb
    # -> /path/to/the/_build/exec_notebook1.ipynb
    # -> /path/to/the/_build/notebook1.html
    nb_name = 'notebook1'
    nb_path = os.path.join(test_root_path, 'data', 'nb_test1',
                           f'{nb_name}.ipynb')
    build_path = os.path.join(test_root_path, 'data', 'nb_test1',
                              BUILD_DIR_NAME)
    nb = NBStaticNotebook(nb_path, build_path)
    assert nb.nb_exec_path == os.path.abspath(os.path.join(
        build_path, f'exec_{nb_name}.ipynb'))
    assert nb.nb_html_path == os.path.abspath(os.path.join(
        build_path, f'{nb_name}.html'))

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
        nb = NBStaticNotebook(nb_path, build_path)
        assert nb.nb_exec_path == os.path.abspath(os.path.join(
            build_path, f'exec_{nb_name}.ipynb'))
        assert nb.nb_html_path == os.path.abspath(os.path.join(
            build_path, f'{nb_name}.html'))

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
        nb = NBStaticNotebook(nb_path, build_path)
        assert nb.nb_exec_path == os.path.abspath(os.path.join(
            build_path, f'nb{i}', f'exec_{nb_name}.ipynb'))
        assert nb.nb_html_path == os.path.abspath(os.path.join(
            build_path, f'nb{i}', f'{nb_name}.html'))

    # notebook: /path/to/the/notebook1.ipynb
    # build: /tmp
    # -> /tmp/exec_notebook1.ipynb
    # -> /tmp/notebook1.html
    nb_name = 'notebook1'
    nb_path = os.path.join(test_root_path, 'data', 'nb_test1',
                           f'{nb_name}.ipynb')
    nb = NBStaticNotebook(nb_path, '/tmp')
    assert nb.nb_exec_path == os.path.join('/tmp', f'exec_{nb_name}.ipynb')
    assert nb.nb_html_path == os.path.join('/tmp', f'{nb_name}.html')

    for i in [1, 2]:
        nb_name = f'notebook{i}'
        nb_path = os.path.join(test_root_path, 'data', 'nb_test2',
                               f'{nb_name}.ipynb')
        nb = NBStaticNotebook(nb_path, '/tmp')
        assert nb.nb_exec_path == os.path.join('/tmp', f'exec_{nb_name}.ipynb')
        assert nb.nb_html_path == os.path.join('/tmp', f'{nb_name}.html')


test_nbstaticnotebook()



"""
/path/to/the/ containing: nb1/notebook1.ipynb, nb2/notebook2.ipynb
-> /path/to/the/_build/nb1/exec_notebook1.ipynb
-> /path/to/the/_build/nb1/notebook1.html
-> /path/to/the/_build/nb2/exec_notebook2.ipynb
-> /path/to/the/_build/nb2/notebook2.html
"""