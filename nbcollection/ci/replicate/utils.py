import git
import os
import logging
import requests
import types
import typing

from datetime import datetime

from nbcollection.ci.constants import ENCODING, AUTH_USERNAME, AUTH_TOKEN, COMMIT_DATE_FORMAT
from nbcollection.ci.generator.datatypes import URLParts
from nbcollection.ci.replicate.datatypes import RemoteParts, GitConfigRemote, GitConfigBranch, \
        GitConfig, PullRequestCommitInfo, PullRequestSource, PullRequestInfo, RepoInfo
from nbcollection.ci.scanner.utils import find_build_jobs

from requests.auth import HTTPBasicAuth

logger = logging.getLogger(__name__)


def parse_git_config(filepath: str) -> GitConfig:
    if not os.path.exists(filepath):
        return None

    options = {}
    remotes = []
    branches = []
    with open(filepath, 'rb') as stream:
        latest_header_type = None
        latest_datas = []
        line_datas = stream.read().decode(ENCODING).split('\n')
        for idx, line in enumerate(line_datas):
            line = line.strip()
            if line.startswith('[') or idx + 1 == len(line_datas):
                if latest_header_type is None:
                    latest_header_type = line

                if len(latest_datas) == 0:
                    continue

                if 'core' in latest_header_type:
                    for entry in latest_datas:
                        head, tail = [item.strip() for item in entry.split('=')]
                        options[head] = tail

                elif 'remote' in latest_header_type:
                    remote_options = {}
                    for entry in latest_datas:
                        head, tail = [item.strip() for item in entry.split('=')]
                        remote_options[head] = tail

                    remote_options['name'] = latest_header_type.split('"')[1]
                    remotes.append(GitConfigRemote(remote_options['name'],
                                                   RemoteParts.ParseURLToRemoteParts(remote_options['url']),
                                                   remote_options['fetch']))

                elif 'branch' in latest_header_type:
                    branch_options = {}
                    for entry in latest_datas:
                        head, tail = [item.strip() for item in entry.split('=')]
                        branch_options[head] = tail

                    branch_options['name'] = latest_header_type.split('"')[1]
                    try:
                        git_remote = [remote for remote in remotes if remote.name == branch_options['remote']][0]
                    except IndexError:
                        git_remote = None

                    branches.append(GitConfigBranch(branch_options['name'], git_remote, branch_options['merge']))

                else:
                    raise NotImplementedError(latest_header_type)

                latest_header_type = line
                latest_datas = []

            else:
                latest_datas.append(line)

    return GitConfig(filepath, options, remotes, branches)


def find_repo_path_by_remote(remote: str, start_path: str) -> str:
    for root, dirnames, filenames in os.walk(start_path):
        if '.git' in dirnames:
            git_config_path = os.path.join(root, '.git', 'config')
            git_config = parse_git_config(git_config_path)
            if git_config:
                for git_remote in git_config.remotes:
                    if git_remote.is_match(remote):
                        return root

        for dirname in dirnames:
            dirpath = os.path.join(root, dirname)
            git_config_path = os.path.join(dirpath, '.git', 'config')
            git_config = parse_git_config(git_config_path)
            if git_config:
                for git_remote in git_config.remotes:
                    if git_remote.is_match(remote):
                        return dirpath

        break


def obtain_pull_request_info(url_parts: URLParts) -> typing.Any:
    url = f'https://api.github.com/repos/{url_parts.org}/{url_parts.repo_name}/pulls/{url_parts.pull_request_number}'
    if AUTH_USERNAME and AUTH_TOKEN:
        auth = HTTPBasicAuth(AUTH_USERNAME, AUTH_TOKEN)

    else:
        auth = None

    response = requests.get(url, auth=auth, headers={
        'Accept': 'application/vnd.github.v3+json'
    })
    if response.status_code not in [200]:
        raise NotImplementedError

    commits_url = '/'.join([
        'https://api.github.com',
        'repos',
        url_parts.org,
        url_parts.repo_name,
        'pulls',
        url_parts.pull_request_number,
        'commits'
    ])
    commits_response = requests.get(commits_url, auth=HTTPBasicAuth(AUTH_USERNAME, AUTH_TOKEN), headers={
        'Accept': 'application/vnd.github.v3+json'
    })
    if commits_response.status_code not in [200]:
        raise NotImplementedError

    commit_infos = []
    for commit in commits_response.json():
        try:
            author = commit['author']['login']
        except Exception:
            raise NotImplementedError

        committer = commit['committer']['login']
        date = datetime.strptime(commit['commit']['author']['date'], COMMIT_DATE_FORMAT)
        if commit['commit']['message'].lower().startswith('merge branch'):
            continue

        commit_infos.append(
                PullRequestCommitInfo(author,
                                      committer,
                                      date,
                                      commit['sha'],
                                      commit['commit']['message']))

    content = response.json()
    source = PullRequestSource(
            content['head']['repo']['owner']['login'],
            content['head']['repo']['name'],
            content['head']['ref'],
            content['head']['label'])
    return PullRequestInfo(content['title'],
                           content['url'],
                           url_parts,
                           [info for info in reversed(commit_infos)],
                           content,
                           source)


def select_build_jobs_by_pr_author_commits(repo_info: RepoInfo, pr_info: PullRequestInfo) -> types.GeneratorType:
    source_files = {}
    for commit in pr_info.commits:
        comms = [c for c in repo_info.repo.iter_commits() if c.hexsha == commit.commit_hash]
        if len(comms) > 1:
            raise NotImplementedError("Shouldn't be possible")

        try:
            comm = comms[0]
        except IndexError:
            continue

        source_files.update(comm.stats.files)

    for path in source_files.keys():
        if not path.endswith('ipynb'):
            continue

        collection_name = path.split('/', 1)[0]
        category_name = os.path.dirname(path).rsplit('/', 1)[1]
        for build_job in find_build_jobs(repo_info.repo.working_dir, [collection_name], [category_name]):
            yield build_job


def select_build_jobs(repo_info: RepoInfo, pr_info: PullRequestInfo) -> types.GeneratorType:
    rel_paths_with_notebooks = []
    for diff in repo_info.repo.index.diff(pr_info.commits[-1].commit_hash):
        rel_path = os.path.dirname(diff.b_path)
        if diff.b_path.endswith('.ipynb'):
            rel_paths_with_notebooks.append(rel_path)

    rel_paths_with_notebooks = [path for path in set(rel_paths_with_notebooks)]
    for path in rel_paths_with_notebooks:
        collection_name = path.split('/', 1)[0]
        category_name = path.rsplit('/', 1)[1]
        for build_job in find_build_jobs(repo_info.repo.working_dir, [collection_name], [category_name]):
            yield build_job


def extract_repo_info(repo: git.Repo, pr_info: PullRequestInfo) -> RepoInfo:
    source_remote = getattr(repo.remotes, pr_info.source.org, None)
    if source_remote is None:  # edge case check
        raise Exception

    logger.info(f'Fetching Remote[{pr_info.source.label}]')
    source_remote.fetch()
    source_ref = getattr(source_remote.refs, pr_info.source.ref, None)
    if source_ref is None:  # edge case check
        raise Exception

    source_head = repo.create_head(pr_info.source.org, source_ref)
    source_head.checkout()
    return RepoInfo(repo, source_remote, source_ref, source_head)
