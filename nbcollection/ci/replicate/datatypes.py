import enum
import git
import typing

from datetime import datetime

from nbcollection.ci.constants import PWN, AUTH_USERNAME, AUTH_TOKEN

from urllib.parse import urlparse


class RepoInfo(typing.NamedTuple):
    repo: git.Repo
    source_remote: git.Remote
    source_ref: git.RemoteReference
    source_head: git.Head


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
            return f'https://{AUTH_USERNAME}:{AUTH_TOKEN}@github.com/{self.org}/{self.repo_name}'


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
                scheme = RemoteScheme.__members__[[
                    sc
                    for sc, sv in RemoteScheme.__members__.items()
                    if sv.value == url_parts.scheme][0]]
            except IndexError:
                raise NotImplementedError(url_parts.scheme)

            org, repo_name, rest = url_parts.path.strip('/').split('/', 2)
            return RemoteParts(scheme, url_parts.netloc, org, repo_name)

        elif url.startswith('http'):
            url_parts = urlparse(url)
            try:
                scheme = RemoteScheme.__members__[[
                    sc
                    for sc, sv in RemoteScheme.__members__.items()
                    if sv.value == url_parts.scheme][0]]
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
        return f'https://{AUTH_USERNAME}:{AUTH_TOKEN}@github.com/{self.org}/{self.name}.git'


class PullRequestInfo(typing.NamedTuple):
    title: str
    url: str
    url_parts: URLParts
    commits: typing.List[PullRequestCommitInfo]
    info: typing.Dict[str, typing.Any]
    source: PullRequestSource


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

