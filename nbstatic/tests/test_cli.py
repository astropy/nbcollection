import os
import pytest

from nbstatic.__main__ import main


@pytest.mark.parametrize('command', ['execute', 'convert'])
def test_default(tmp_path, command):
    test_root_path = os.path.dirname(__file__)

    nb_name = 'notebook1.ipynb'
    nb_path = os.path.join(test_root_path, f'data/nb_test1/{nb_name}')
    nb_root_path = os.path.split(nb_path)[0]
    counter = 0

    # Default behavior, one notebook input, no specified build path
    _ = main(['nbstatic', command, nb_path])
    assert '_build' in os.listdir(nb_root_path)
    assert nb_name in os.listdir(os.path.join(nb_root_path, '_build'))

    # Default behavior, one notebook input, specified build path
    build_path = tmp_path / f'test_{command}_{counter}'
    counter += 1
    build_path.mkdir()
    _ = main(['nbstatic', command, nb_path,
              f'--build-path={str(build_path)}'])
    assert '_build' in os.listdir(str(build_path))
    assert nb_name in os.listdir(os.path.join(build_path, '_build'))

    # Default behavior, one notebook path, no specified build path
    _ = main(['nbstatic', command, nb_root_path])
    assert '_build' in os.listdir(os.path.join(nb_root_path, '..'))
    assert nb_name in os.listdir(os.path.join(nb_root_path,
                                              '../_build/nb_test1'))

    # Default behavior, one notebook path, specified build path
    build_path = tmp_path / f'test_{command}_{counter}'
    counter += 1
    build_path.mkdir()
    _ = main(['nbstatic', command, nb_root_path,
              f'--build-path={str(build_path)}'])
    assert '_build' in os.listdir(str(build_path))
    assert nb_name in os.listdir(os.path.join(build_path, '_build/nb_test1'))

    # Default behavior, two notebook files, no specified build path
    nb_path1 = os.path.join(test_root_path, 'data/nb_test1/notebook1.ipynb')
    nb_path2 = os.path.join(test_root_path, 'data/nb_test2/notebook2.ipynb')
    build_path = tmp_path / f'test_{command}_{counter}'
    counter += 1
    build_path.mkdir()
    _ = main(['nbstatic', command, nb_path1, nb_path2,
              f'--build-path={str(build_path)}'])
    assert '_build' in os.listdir(str(build_path))
    for nb_name in ['notebook1.ipynb', 'notebook2.ipynb']:
        assert nb_name in os.listdir(os.path.join(build_path, '_build'))


@pytest.mark.parametrize('command', ['execute', 'convert'])
def test_flatten(tmp_path, command):
    test_root_path = os.path.dirname(__file__)

    nb_root_path = os.path.join(test_root_path, 'data/my_notebooks')

    # One notebook path, no specified build path, but flatten the file structure
    _ = main(['nbstatic', command, nb_root_path, '--flatten'])
    assert '_build' in os.listdir(os.path.join(nb_root_path, '..'))
    for nb_name in ['notebook1', 'notebook2', 'notebook3']:
        assert f'{nb_name}.ipynb' in os.listdir(os.path.join(nb_root_path,
                                                             '../_build/'))

        if command == 'convert':
            assert f'{nb_name}.html' in os.listdir(os.path.join(nb_root_path,
                                                                '../_build/'))


# Too scary...
# def teardown_module():
#     for path in BUILD_PATHS:
#         if path is not None and os.path.exists(path):
#             print(f"Test cleanup: Removing {path}")
#             shutil.rmtree(path)
