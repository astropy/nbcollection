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

@pytest.fixture
def single_collection_repo(request: SubRequest):
    single_collection_repo = TestRepo(RepoType.Local, Template.SingleCollection)
    request.addfinalizer(single_collection_repo.destroy)
    return single_collection_repo.setup().repo_path

@pytest.fixture
def multi_collection_repo(request: SubRequest):
    multi_collection_repo = TestRepo(RepoType.Local, Template.MultiCollection)
    request.addfinalizer(multi_collection_repo.destroy)
    return multi_collection_repo.setup().repo_path

@pytest.fixture
def single_collection_repo__immediate_categories(request: SubRequest) -> str:
    immediate_categories_repo = TestRepo(RepoType.Local, Template.SingleCollectionImmediateCategories)
    request.addfinalizer(immediate_categories_repo.destroy)
    return immediate_categories_repo.setup().repo_path

@pytest.fixture
def single_collection_repo__nth_categories(request: SubRequest) -> str:
    nth_categories_repo = TestRepo(RepoType.Local, Template.SingleCollectionNthCategories)
    request.addfinalizer(nth_categories_repo.destroy)
    return nth_categories_repo.setup().repo_path

@pytest.fixture
def quick_build_collection(request: SubRequest) -> str:
    quick_build_repo = TestRepo(RepoType.Local, Template.QuickBuild)
    request.addfinalizer(quick_build_repo.destroy)
    return quick_build_repo.setup().repo_path

@pytest.fixture
def executed_notebook_collection(request: SubRequest) -> str:
    executed_notebook_repo = TestRepo(RepoType.Local, Template.ExecutedCollection)
    request.addfinalizer(executed_notebook_repo.destroy)
    return executed_notebook_repo.setup().repo_path
