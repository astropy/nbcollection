import os
import shutil
import pytest

from nbstatic.__main__ import main

BUILD_PATHS = []


@pytest.mark.parametrize('command', ['execute', 'convert'])
def test_execute(tmp_path, command):
    test_root_path = os.path.dirname(__file__)

    nb_name = 'notebook1.ipynb'
    nb_path = os.path.join(test_root_path, f'data/nb_test1/{nb_name}')
    nb_root_path = os.path.split(nb_path)[0]
    counter = 0

    # Default behavior, one notebook input, no specified build path
    _ = main(['nbstatic', command, nb_path])
    assert '_build' in os.listdir(nb_root_path)
    assert nb_name in os.listdir(os.path.join(nb_root_path, '_build'))
    BUILD_PATHS.append(os.path.join(nb_root_path, '_build'))

    # Default behavior, one notebook input, specified build path
    build_path = tmp_path / f'test_{command}_{counter}'
    counter += 1
    build_path.mkdir()
    _ = main(['nbstatic', command, nb_path,
              f'--build-path={str(build_path)}'])
    assert '_build' in os.listdir(str(build_path))
    assert nb_name in os.listdir(os.path.join(build_path, '_build'))
    BUILD_PATHS.append(os.path.join(build_path, '_build'))

    # Default behavior, one notebook path, no specified build path
    _ = main(['nbstatic', command, nb_root_path])
    assert '_build' in os.listdir(os.path.join(nb_root_path, '..'))
    assert nb_name in os.listdir(os.path.join(nb_root_path,
                                              '../_build/nb_test1'))
    BUILD_PATHS.append(os.path.join(nb_root_path, '../_build'))

    # Default behavior, one notebook path, specified build path
    build_path = tmp_path / f'test_{command}_{counter}'
    counter += 1
    build_path.mkdir()
    _ = main(['nbstatic', command, nb_root_path,
              f'--build-path={str(build_path)}'])
    assert '_build' in os.listdir(str(build_path))
    assert nb_name in os.listdir(os.path.join(build_path, '_build/nb_test1'))
    BUILD_PATHS.append(os.path.join(build_path, '_build'))


def teardown_module():
    for path in BUILD_PATHS:
        if build_path is not None and os.path.exists(build_path):
            shutil.rmtree(build_path)