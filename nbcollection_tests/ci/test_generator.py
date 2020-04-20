import pytest
import typing

from nbcollection_tests.ci.tools import repo_local_path, repo_git_url, repo_https_url
from nbcollection_tests.ci.tools.utils import hash_filesystem

PWN: typing.TypeVar = typing.TypeVar('PWN')

def test__select_repo_path_type__Local(repo_local_path: str) -> None:
    import git
    import os
    import tempfile

    from nbcollection.ci.generator.datatypes import select_repo_path_type, RepoPathType

    repo_path, repo_path_type = select_repo_path_type(repo_local_path)
    assert repo_path_type is RepoPathType.Local
    assert os.path.exists(repo_path)
    try:
        git.Repo(repo_path)
    except git.exc.InvalidGitRepository:
        raise NotImplementedError

def test__select_repo_path_type__Github_git_url(repo_git_url: str) -> None:
    import os

    from nbcollection.ci.generator.datatypes import select_repo_path, RepoType

    repo_path, repo_type = select_repo_path(repo_https_url)
    assert not os.path.exists(repo_path)
    assert repo_type == RepoPathType.GithubGIT

def test__select_repo_path_type__Github_https_url(repo_https_url: str) -> None:
    import os

    from nbcollection.ci.generator.datatypes import select_repo_path, RepoType

    repo_path, repo_type = select_repo_path(repo_https_url)
    assert not os.path.exists(repo_path)
    assert repo_type is RepoPathType.GithubHTTPS

def test__Repo__Local(repo_local_path: str) -> None:
    import git
    import os

    from nbcollection.ci.generator.datatypes import Repo

    class LocalRepoTest(Repo):
        pass

    repo_path_hash: str = hash_filesystem(repo_local_path)
    with LocalRepoTest(repo_local_path) as repo:
        assert repo.repo_path == repo_local_path
        assert os.path.exists(repo.repo_path)
        try:
            git_repo = git.Repo(repo.repo_path)
        except (
            git.exc.NoSuchPathError,
            git.exc.InvalidGitRepositoryError) as err:
            pytest.fail(f'RepoPath[{repo_local_path}] is not a GitRepo')

        fs_hash: str = hash_filesystem(repo.repo_path)
        # Check to make sure nothing is copied into the FileSystem when creating the Local Repo object type
        if repo_path_hash != fs_hash:
            pytest.fail('FileSystem should not have been altered')

        # Check Install. Should do nothing
        try:
            repo.install()
        except NotImplementedError:
            if fs_hash != hash_filesystem(repo.repo_path):
                pytest.fail('FileSystem should not have been altered')

        else:
            pytest.fail('Method should have raised error')

        # Check Uninstall. Should do nothing
        try:
            repo.uninstall()
        except NotImplementedError:
            if fs_hash != hash_filesystem(repo.repo_path):
                pytest.fail('FileSystem should not have been altered')
        else:
            pytest.fail('Method should have raised error')



def test__Repo__Github__git_url(repo_git_url: str) -> None:
    import git
    import os

    from nbcollection.ci.generator.datatypes import Repo

    class GithubGITRepoTest(Repo):
        pass
  
    repo = GithubGITRepoTest(repo_git_url)
    repo_path_hash: str = hash_filesystem(repo.repo_path)
    with repo as repo:
        repo_path_hash__after_github_checkout = hash_filesystem(repo.repo_path)
        if repo_path_hash == repo_path_hash__after_github_checkout:
            pytest.fail('FileSystem should have been altered')

    if repo_path_hash == hash_filesystem(repo.repo_path):
        pytest.fail('FileSystem should have been altered')

    if repo_path_hash__after_github_checkout != hash_filesystem(repo.repo_path):
        pytest.fail('FileSystem should not have been altered')


def test__Repo__Github__https_url(repo_https_url: str) -> None:
    import git
    import os

    from nbcollection.ci.generator.datatypes import Repo

    class GithubHTTPSRepoTest(Repo):
        pass
  
    repo = GithubHTTPSRepoTest(repo_https_url)
    repo_path_hash: str = hash_filesystem(repo.repo_path)
    with repo as repo:
        repo_path_hash__after_github_checkout = hash_filesystem(repo.repo_path)
        if repo_path_hash == repo_path_hash__after_github_checkout:
            pytest.fail('FileSystem should have been altered')

    if repo_path_hash == hash_filesystem(repo.repo_path):
        pytest.fail('FileSystem should have been altered')

    if repo_path_hash__after_github_checkout != hash_filesystem(repo.repo_path):
        pytest.fail('FileSystem should not have been altered')

def test__CircleCiRepo__install(repo_local_path: str) -> None:
    from nbcollection.ci.exceptions import InstallException
    from nbcollection.ci.generator.circle_ci import CircleCiRepo

    fs_hash: str = hash_filesystem(repo_local_path)
    with CircleCiRepo(repo_local_path) as repo:
        assert fs_hash == hash_filesystem(repo.repo_path)
        try:
            repo.install()
        except InstallException:
            assert fs_hash == hash_filesystem(repo.repo_path)
            repo.install(overwrite=True)

        else:
            pytest.fail('.circle-ci directory should already exists in this test. Is the testing Repo incorrect?')

        assert fs_hash != hash_filesystem(repo.repo_path)

def test__CircleCiRepo__uninstall(repo_local_path: str) -> None:
    from nbcollection.ci.exceptions import InstallException
    from nbcollection.ci.generator.circle_ci import CircleCiRepo

    fs_hash: str = hash_filesystem(repo_local_path)
    with CircleCiRepo(repo_local_path) as repo:
        assert fs_hash == hash_filesystem(repo.repo_path)
        repo.install(overwrite=True)
        fs_hash__after_install = hash_filesystem(repo.repo_path)
        assert fs_hash != fs_hash__after_install

        repo.uninstall()
        fs_hash__after_install != hash_filesystem(repo_local_path)

