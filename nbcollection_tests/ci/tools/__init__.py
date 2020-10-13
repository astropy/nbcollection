import pytest
import typing

from _pytest.fixtures import SubRequest
from nbcollection_tests.ci.tools.integrations import TestRepo
from nbcollection_tests.ci.tools.integrations.datatypes import Template, RepoType

@pytest.fixture
def repo_local_path(request: SubRequest) -> str:
    local_repo = TestRepo(RepoType.Local, Template.Initial)
    request.addfinalizer(local_repo.destroy)
    return local_repo.setup().repo_path

@pytest.fixture
def repo_git_url(request: SubRequest) -> str:
    remote_repo = TestRepo(RepoType.Github, Template.Initial)
    request.addfinalizer(remote_repo.destroy)
    return remote_repo.setup().git_url

@pytest.fixture
def repo_https_url(request: SubRequest) -> str:
    remote_repo = TestRepo(RepoType.Github, Template.Initial)
    request.addfinalizer(remote_repo.destroy)
    return remote_repo.setup().https_url

@pytest.fixture
def multi_level_ignore_repo(request: SubRequest):
    ignore_repo = TestRepo(RepoType.Local, Template.MultiLevelIgnore)
    request.addfinalizer(ignore_repo.destroy)
    return ignore_repo.setup().repo_path
