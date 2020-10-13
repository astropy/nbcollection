import pytest
import typing

from _pytest.fixtures import SubRequest
from nbcollection_tests.ci.tools import integrations

@pytest.fixture
def repo_local_path(request: SubRequest) -> str:
    local_repo = integrations.TestRepo(integrations.RepoType.Local, integrations.Template.Initial)
    request.addfinalizer(local_repo.destroy)
    return local_repo.setup().repo_path

@pytest.fixture
def repo_git_url(request: SubRequest) -> str:
    remote_repo = integrations.TestRepo(integrations.RepoType.Github, integrations.Template.Initial)
    request.addfinalizer(remote_repo.destroy)
    return remote_repo.setup().git_url

@pytest.fixture
def repo_https_url(request: SubRequest) -> str:
    remote_repo = integrations.TestRepo(integrations.RepoType.Github, integrations.Template.Initial)
    request.addfinalizer(remote_repo.destroy)
    return remote_repo.setup().https_url

@pytest.fixture
def multi_level_ignore_repo(request: SubRequest):
    ignore_repo = integrations.TestRepo(integrations.RepoType.Local, integrations.Template.MultiLevelIgnore)
    request.addfinalizer(ignore_repo)
    return ignore_repo.setup().repo_path
