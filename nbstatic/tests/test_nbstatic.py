import os

from nbstatic.convert import NBStaticNotebook, BUILD_DIR_NAME


def test_nbstaticnotebook():
    test_root_path = os.path.dirname(__file__)

    nb_path = os.path.join(test_root_path, 'data', 'nb_test1',
                           'notebook1.ipynb')
    build_path = os.path.join(test_root_path, 'data', 'nb_test1',
                              BUILD_DIR_NAME)
    nb = NBStaticNotebook(nb_path, build_path)
    print(nb.nb_exec_path)
    print(nb.nb_html_path)
    return

    nb = NBStaticNotebook(nb_path, root_path)
    print(nb.nb_build_path)
    # assert nb.nb_build_path == os.path.join(BUILD_DIR, 'the', 'notebook.ipynb')


test_nbstaticnotebook()



"""
/path/to/the/notebook.ipynb
-> /path/to/the/_build/exec_notebook.ipynb
-> /path/to/the/_build/notebook.html

/path/to/the/ containing: notebook1.ipynb, notebook2.ipynb
-> /path/to/the/_build/exec_notebook1.ipynb
-> /path/to/the/_build/notebook1.html
-> /path/to/the/_build/exec_notebook2.ipynb
-> /path/to/the/_build/notebook2.html

/path/to/the/ containing: nb1/notebook1.ipynb, nb2/notebook2.ipynb
-> /path/to/the/_build/nb1/exec_notebook1.ipynb
-> /path/to/the/_build/nb1/notebook1.html
-> /path/to/the/_build/nb2/exec_notebook2.ipynb
-> /path/to/the/_build/nb2/notebook2.html
"""