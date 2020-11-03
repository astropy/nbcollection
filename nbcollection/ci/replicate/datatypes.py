import argparse
import enum
import git
import jinja2
import logging
import os
import tempfile
import typing

from nbcollection.ci import exceptions as ci_exceptions
from nbcollection.ci.constants import DEFAULT_REMOTE, DEFAULT_BRANCH, PWN
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

class RemoteScheme(enum.Enum):
    Git = 'git'
    Http = 'http'
    Https = 'https'

class RemoteParts(typing.NamedTuple):
    scheme: RemoteScheme
    netloc: str
    org: str
    name: str

    @classmethod
    def ParseURLToRemoteParts(cls: PWN, url: str) -> PWN:
        if url.startswith('git@'):
            netloc = url.split('@', 1)[1].rsplit(':', 1)[0]
            path = url.rsplit(':', 1)[1]
            if path.endswith('.git'):
                path = path[:-4]

            org, repo_name = path.split('/', 1)
            return cls(RemoteScheme.Git, netloc, org, repo_name)

        elif url.startswith('http') and url.endswith('.git'):
            url_parts = urlparse(url)
            try:
                scheme = RemoteScheme.__members__[[sc for sc, sv in RemoteScheme.__members__.items() if sv.value == url_parts.scheme][0]]
            except IndexError:
                raise NotImplementedError(url_parts.scheme)

            org, repo_name = url_parts.path.rsplit('.git', 1)[0].strip('/').split('/')
            return RemoteParts(scheme, url_parts.netloc, org, repo_name)

        elif url.startswith('http') and 'pull/' in url:
            url_parts = urlparse(url)
            try:
                scheme = RemoteScheme.__members__[[sc for sc, sv in RemoteScheme.__members__.items() if sv.value == url_parts.scheme][0]]
            except IndexError:
                raise NotImplementedError(url_parts.scheme)

            org, repo_name, rest = url_parts.path.strip('/').split('/', 2)
            return RemoteParts(scheme, url_parts.netloc, org, repo_name)

        else:
            raise NotImplementedError(url)

class GitConfigRemote(typing.NamedTuple):
    name: str
    parts: RemoteParts
    fetch: str
    def is_match(self: PWN, url: str) -> bool:
        other_remote_parts = RemoteParts.ParseURLToRemoteParts(url)
        return other_remote_parts.netloc == self.parts.netloc and \
                other_remote_parts.org == self.parts.org and \
                other_remote_parts.name == self.parts.name

class GitConfigBranch(typing.NamedTuple):
    name: str
    remote: GitConfigRemote
    merge: str

class GitConfig(typing.NamedTuple):
    filepath: str
    options: typing.Dict[str, str]
    remotes: typing.List[GitConfigRemote]
    branches: typing.List[GitConfigBranch]
