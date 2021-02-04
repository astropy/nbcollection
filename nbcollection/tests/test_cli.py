import os
import pytest

from nbcollection.__main__ import main


@pytest.mark.parametrize('command', ['execute', 'convert'])
def test_default(tmp_path, command):
    test_root_path = os.path.dirname(__file__)

    nb_name = 'notebook1.ipynb'
    nb_path = os.path.join(test_root_path, f'data/nb_test1/{nb_name}')
    nb_root_path = os.path.split(nb_path)[0]
    counter = 0

    # Default behavior, one notebook input, no specified build path
    _ = main(['nbcollection', command, nb_path])
    if '_build' not in os.listdir(nb_root_path):
        raise Exception

    if nb_name not in os.listdir(os.path.join(nb_root_path, '_build')):
        raise Exception

    # Default behavior, one notebook input, specified build path
    build_path = tmp_path / f'test_{command}_{counter}'
    counter += 1
    build_path.mkdir()
    _ = main(['nbcollection', command, nb_path,
              f'--build-path={str(build_path)}'])
    if '_build' not in os.listdir(str(build_path)):
        raise Exception

    if nb_name not in os.listdir(os.path.join(build_path, '_build')):
        raise Exception

    # Default behavior, one notebook path, no specified build path
    _ = main(['nbcollection', command, nb_root_path])
    if '_build' not in os.listdir(os.path.join(nb_root_path, '..')):
        raise Exception

    if nb_name not in os.listdir(os.path.join(nb_root_path, '../_build/nb_test1')):
        raise Exception

    # Default behavior, one notebook path, specified build path
    build_path = tmp_path / f'test_{command}_{counter}'
    counter += 1
    build_path.mkdir()
    _ = main(['nbcollection', command, nb_root_path,
              f'--build-path={str(build_path)}'])
    if '_build' not in os.listdir(str(build_path)):
        raise Exception
    if nb_name not in os.listdir(os.path.join(build_path, '_build/nb_test1')):
        raise Exception

    # Two notebook files, specified build path
    nb_path1 = os.path.join(test_root_path, 'data/nb_test1/notebook1.ipynb')
    nb_path2 = os.path.join(test_root_path, 'data/nb_test2/notebook2.ipynb')
    build_path = tmp_path / f'test_{command}_{counter}'
    counter += 1
    build_path.mkdir()
    _ = main(['nbcollection', command, f'--build-path={str(build_path)}',
              nb_path1, nb_path2])
    if '_build' not in os.listdir(str(build_path)):
        raise Exception

    for nb_name in ['notebook1.ipynb', 'notebook2.ipynb']:
        if nb_name not in os.listdir(os.path.join(build_path, '_build')):
            raise Exception


@pytest.mark.parametrize('command', ['execute', 'convert'])
def test_flatten(tmp_path, command):
    test_root_path = os.path.dirname(__file__)

    nb_root_path = os.path.join(test_root_path, 'data/my_notebooks')

    # One notebook path, no specified build path, but flatten the file structure
    _ = main(['nbcollection', command, nb_root_path, '--flatten'])
    if '_build' not in os.listdir(os.path.join(nb_root_path, '..')):
        raise Exception
    for nb_name in ['notebook1', 'notebook2', 'notebook3']:
        if f'{nb_name}.ipynb' not in os.listdir(os.path.join(nb_root_path, '../_build/')):
            raise Exception

        if command == 'convert':
            if f'{nb_name}.html' not in os.listdir(os.path.join(nb_root_path, '../_build/')):
                raise Exception


def test_index(tmp_path):
    test_root_path = os.path.dirname(__file__)

    nb_root_path = os.path.join(test_root_path, 'data/my_notebooks')
    index_tpl_path = os.path.join(test_root_path, 'data/default.tpl')

    # Make an index file with more complex notebook path structure
    build_path = tmp_path / 'test_index'
    _ = main(['nbcollection', 'convert', nb_root_path,
              f'--build-path={str(build_path)}',
              '--make-index', f'--index-template={index_tpl_path}'])
    if '_build' not in os.listdir(str(build_path)):
        raise Exception

    if 'index.html' not in os.listdir(str(build_path / '_build')):
        raise Exception

    # Flatten the build directory structure and make an index file
    _ = main(['nbcollection', 'convert', nb_root_path, '--flatten',
              '--make-index', f'--index-template={index_tpl_path}'])
    if '_build' not in os.listdir(os.path.join(nb_root_path, '..')):
        raise Exception

    build_path = os.path.join(nb_root_path, '../_build/')
    if 'index.html' not in os.listdir(build_path):
        raise Exception


# Too scary...
# def teardown_module():
#     for path in BUILD_PATHS:
#         if path is not None and os.path.exists(path):
#             print(f"Test cleanup: Removing {path}")
#             shutil.rmtree(path)
