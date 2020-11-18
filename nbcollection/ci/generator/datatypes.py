import argparse
import enum
import git
import jinja2
import logging
import os
import tempfile
import typing

from nbcollection.ci import exceptions as ci_exceptions
from nbcollection.ci.constants import DEFAULT_REMOTE, DEFAULT_BRANCH, PWN, GITHUB_USERNAME, GITHUB_TOKEN
from nbcollection.ci.template import ENVIRONMENT

from urllib.parse import urlparse

PWN: typing.TypeVar = typing.TypeVar('PWN')
logger = logging.getLogger(__name__)

class RepoType(enum.Enum):
    Local = 'local-path'
    GithubGIT = 'github-git'
    GithubHTTPS = 'github-https'

class URLType(enum.Enum):
    GithubRepoURL = 'github-repo-url'
    GithubPullRequest = 'github-pull-request'

class URLParts(typing.NamedTuple):
    url_type: URLType
    org: str
    repo_name: str
    pull_request_number: int = 0

    @property
    def https_url(self: PWN) -> str:
        if self.url_type in [URLType.GithubPullRequest, URLType.GithubPullRequest]:
            return f'https://github.com/{self.org}/{self.repo_name}'

        raise NotImplementedError(self.url_type)

    @property
    def https_url_with_auth(self: PWN) -> str:
        if self.url_type in [URLType.GithubPullRequest, URLType.GithubPullRequest]:
            return f'https://{GITHUB_USERNAME}:{GITHUB_TOKEN}@github.com/{self.org}/{self.repo_name}'

def select_url_type(url: str, repo_type: RepoType) -> URLParts:
    # https://github.com/spacetelescope/dat_pyinthesky/pull/125
    if repo_type in [RepoType.GithubGIT, RepoType.GithubHTTPS]:
        url_parts = urlparse(url)
        try:
            org, repo_name, rest = url_parts.path.strip('/').split('/', 2)
        except ValueError:
            org, repo_name = url_parts.path.strip('/').split('/', 2)
            rest = None

        if rest is None:
            return URLParts(URLType.GithubRepoURL, org, repo_name, 0)

        elif rest.startswith('pull'):
            pr_num = rest.strip('pull/').split('/', 1)[0]
            if '/' in pr_num:
                raise NotImplementedError(f'Unable to parse pr_num[{pr_num}]')

            return URLParts(URLType.GithubPullRequest, org, repo_name, pr_num)

        else:
            raise NotImplementedError

    else:
        raise NotImplementedError(repo_type)

def select_repo_type(repo_path: str) -> typing.Tuple[str, RepoType]:
    if os.path.exists(repo_path):
        try:
            git.Repo(repo_path)
        except git.exc.InvalidGitRepositoryError:
            raise ci_exceptions.InvalidRepoPath(f'RepoPath[{repo_path}] is not a Repository')

        else:
            return repo_path, RepoType.Local

    elif repo_path.startswith('git@github.com'):
        return tempfile.NamedTemporaryFile().name, RepoType.GithubGIT

    elif repo_path.startswith('https://github.com'):
        return tempfile.NamedTemporaryFile().name, RepoType.GithubHTTPS

    else:
        raise ci_exceptions.InvalidRepoPath(f'RepoPath[{repo_path}] does not exist')

class Repo:
    repo_path: str
    repo_url: str
    repo_type: RepoType
    _altered_files: typing.List[str]

    def _sync_repo_locally(self: PWN) -> None:
        if self.repo_type is RepoType.Local:
            pass

        elif self.repo_type is RepoType.GithubGIT:
            logger.info(f'Cloning Repo[{self.repo_url}] to Path[{self.repo_path}]')
            git.Repo.clone_from(self.repo_url, self.repo_path)

        elif self.repo_type is RepoType.GithubHTTPS:
            git.Repo.clone_from(self.repo_url, self.repo_path)

        else:
            raise NotImplementedError(self.repo_type)

    def _sync_repo_remote(self: PWN) -> None:
        if self.repo_type is RepoType.Local:
            pass

        elif self.repo_type is RepoType.GithubGIT:
            logger.info(f'Syncing new files from LocalRepo to GithubRepo[{self.repo_url}]')
            repo: git.repo.base.Repo = git.Repo(self.repo_path)
            for filepath in self._altered_files:
                repo.git.add(filepath)

            if len(repo.index.diff('origin/master')) or len(self._altered_files) > 0:
                repo.index.commit('Added by CircleCI Integration from https://github.com/adrn/nbcollection')
                remote: git.Remote = repo.remote(name='origin')
                remote.push()

        elif self.repo_type is RepoType.GithubHTTPS:
            repo = git.Repo(self.repo_path)
            for filepath in self._altered_files:
                repo.git.add(filepath)

            # if len(repo.index.diff('origin/main')) or len(self._altered_files) > 0:
            if len(repo.index.diff(f'{DEFAULT_REMOTE}/{DEFAULT_BRANCH}')):
                repo.index.commit('Added by CircleCI Integration from https://github.com/adrn/nbcollection')
                remote: git.Remote = repo.remote(name='origin')
                remote.push()

        else:
            raise NotImplementedError(self.repo_type)

    def __init__(self: PWN, repo_path: str) -> None:
        self.repo_path, self.repo_type = select_repo_type(repo_path)
        self.repo_url = None if self.repo_type is RepoType.Local else repo_path
        self._altered_files = []

    def __enter__(self: PWN) -> PWN:
        self._sync_repo_locally()
        return self

    def __exit__(self: PWN, type, value, traceback) -> None:
        self._sync_repo_remote()

    def install(self: PWN) -> None:
        raise NotImplementedError

    def uninstall(self: PWN) -> None:
        raise NotImplementedError
