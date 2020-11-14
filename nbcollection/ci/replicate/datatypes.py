import argparse
import enum
import git
import jinja2
import logging
import os
import tempfile
import typing

from datetime import datetime

from nbcollection.ci import exceptions as ci_exceptions
from nbcollection.ci.constants import PWN, GITHUB_USERNAME, GITHUB_TOKEN
from nbcollection.ci.generator.datatypes import URLParts

from urllib.parse import urlparse

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

        elif url.startswith('http') and 'pull/' in url:
            url_parts = urlparse(url)
            try:
                scheme = RemoteScheme.__members__[[sc for sc, sv in RemoteScheme.__members__.items() if sv.value == url_parts.scheme][0]]
            except IndexError:
                raise NotImplementedError(url_parts.scheme)

            org, repo_name, rest = url_parts.path.strip('/').split('/', 2)
            return RemoteParts(scheme, url_parts.netloc, org, repo_name)

        elif url.startswith('http'):
            url_parts = urlparse(url)
            try:
                scheme = RemoteScheme.__members__[[sc for sc, sv in RemoteScheme.__members__.items() if sv.value == url_parts.scheme][0]]
            except IndexError:
                raise NotImplementedError(url_parts.scheme)

            org, repo_name = url_parts.path.rsplit('.git', 1)[0].strip('/').split('/')
            return RemoteParts(scheme, url_parts.netloc, org, repo_name)

        else:
            raise NotImplementedError(url)

    def is_match(self: PWN, url: str) -> bool:
        other_remote_parts = self.__class__.ParseURLToRemoteParts(url)
        return other_remote_parts.netloc == self.netloc and \
                other_remote_parts.org == self.org and \
                other_remote_parts.name == self.name

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

class PullRequestCommitInfo(typing.NamedTuple):
    author: str
    committer: str
    date: datetime
    commit_hash: str
    message: str

class PullRequestSource(typing.NamedTuple):
    org: str
    name: str
    ref: str
    label: str

    @property
    def https_url(self: PWN) -> str:
        return f'https://github.com/{self.org}/{self.name}.git'

    @property
    def https_url_with_auth(self: PWN) -> str:
        return f'https://{GITHUB_USERNAME}:{GITHUB_TOKEN}@github.com/{self.org}/{self.name}.git'

class PullRequestInfo(typing.NamedTuple):
    title: str
    url: str
    url_parts: URLParts
    commits: typing.List[PullRequestCommitInfo]
    info: typing.Dict[str, typing.Any]
    source: PullRequestSource

class RepoInfo(typing.NamedTuple):
    repo: git.Repo
    source_remote: git.Remote
    source_ref: git.RemoteReference
    source_head: git.Head
