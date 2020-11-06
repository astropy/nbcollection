import argparse
import git
import logging
import os
import requests
import types
import typing

from datetime import datetime

from nbcollection.ci.constants import GITHUB_USERNAME, GITHUB_TOKEN, PWN, COMMIT_DATE_FORMAT
from nbcollection.ci.replicate.utils import find_repo_path_by_remote
from nbcollection.ci.replicate.datatypes import RemoteParts, PullRequestCommitInfo, PullRequestSource, PullRequestInfo, RepoInfo
from nbcollection.ci.generator.datatypes import select_repo_type, select_url_type, URLType, RepoType, URLParts
from nbcollection.ci.scanner.utils import find_build_jobs
from nbcollection.ci.venv import virtual_env

from requests.auth import HTTPBasicAuth

logger = logging.getLogger(__name__)

def obtain_pull_request_info(url_parts: URLParts) -> typing.Any:
    url = f'https://api.github.com/repos/{url_parts.org}/{url_parts.repo_name}/pulls/{url_parts.pull_request_number}'
    if GITHUB_USERNAME and GITHUB_TOKEN:
        auth = HTTPBasicAuth(GITHUB_USERNAME, GITHUB_TOKEN)

    else:
        auth = None

    response = requests.get(url, auth=auth, headers={
        'Accept': 'application/vnd.github.v3+json'
    })
    if not response.status_code in [200]:
        import pdb; pdb.set_trace()
        raise NotImplementedError

    commits_url = f'https://api.github.com/repos/{url_parts.org}/{url_parts.repo_name}/pulls/{url_parts.pull_request_number}/commits'
    commits_response = requests.get(commits_url, auth=HTTPBasicAuth(GITHUB_USERNAME, GITHUB_TOKEN), headers={
        'Accept': 'application/vnd.github.v3+json'
    })
    if not commits_response.status_code in [200]:
        raise NotImplementedError

    commit_infos = []
    for commit in commits_response.json():
        try:
            author = commit['author']['login']
        except Exception:
            raise NotImplementedError

        committer = commit['committer']['login']
        date = datetime.strptime(commit['commit']['author']['date'], COMMIT_DATE_FORMAT)
        commit_infos.append(
                PullRequestCommitInfo(author, committer, date,
                    commit['commit']['tree']['sha'],
                    commit['commit']['message']))

    content = response.json()
    source = PullRequestSource(
            content['head']['repo']['owner']['login'],
            content['head']['repo']['name'],
            content['head']['ref'],
            content['head']['label'])
    return PullRequestInfo(content['title'], content['url'], url_parts, [info for info in reversed(commit_infos)], content, source)

def run_replication(options: argparse.Namespace):
    repo_path, repo_type = select_repo_type(options.repo_path)
    url_parts = select_url_type(options.repo_path, repo_type)
    if url_parts.url_type is URLType.GithubPullRequest:
        repo_path = find_repo_path_by_remote(options.repo_path, options.project_path)
        if repo_path is None:
            repo_path = os.path.join(options.project_path, url_parts.org, url_parts.repo_name)

        if os.path.exists(repo_path):
            import shutil
            shutil.rmtree(repo_path)
            pull_request_info = obtain_pull_request_info(url_parts)

        logger.info(f'Loading Pull Request [{url_parts.pull_request_number}] info for {url_parts.org}/{url_parts.repo_name} in {repo_path}')
        pr_info = obtain_pull_request_info(url_parts)
        logger.info(f'Replicating Pull Request [{pr_info.title}] from {url_parts.org}/{url_parts.repo_name}')
        if os.path.exists(repo_path):
            raise NotImplementedError

        else:
            git.Repo.clone_from(url_parts.https_url, repo_path)
            repo = git.Repo(repo_path)
            source_remote = None
            for remote in repo.remotes:
                remote_parts = RemoteParts.ParseURLToRemoteParts(remote.url)
                if remote_parts.org == pr_info.source.org:
                    if remote_parts.repo_name == pr_info.source.name:
                        source_remote = remote
                        break

            if source_remote is None:
                logger.info(f'Attaching PR Source[{pr_info.source.label}] Remote')
                repo.create_remote(pr_info.source.org, pr_info.source.https_url)

            source_remote = getattr(repo.remotes, pr_info.source.org, None)
            assert not source_remote is None # edge case check
            logger.info(f'Fetching Remote[{pr_info.source.label}]')
            source_remote.fetch()
            source_ref = getattr(source_remote.refs, pr_info.source.ref, None)
            assert not source_ref is None # edge case check
            source_head = repo.create_head(pr_info.source.org, source_ref)
            source_head.checkout()
            repo_info = RepoInfo(repo, source_remote, source_ref, source_head)

    else:
        raise NotImplementedError(url_parts.url_type)

    for idx, build_job in enumerate(select_build_jobs(repo_info, pr_info)):
        if idx > 0:
            raise NotImplementedError

        virtual_env.enable(build_job, repo_info, pr_info)

def select_build_jobs(repo_info: RepoInfo, pr_info: PullRequestInfo) -> types.GeneratorType:
    rel_paths_with_notebooks = []
    for diff in repo_info.repo.index.diff(pr_info.commits[-1].commit_hash):
        rel_path = os.path.dirname(diff.b_path)
        if diff.b_path.endswith('.ipynb'):
            rel_paths_with_notebooks.append(rel_path)

    rel_paths_with_notebooks = [path for path in set(rel_paths_with_notebooks)]
    build_job_inputs = []
    for path in rel_paths_with_notebooks:
        collection_name = path.split('/', 1)[0]
        category_name = path.rsplit('/', 1)[1]
        if len(path.split('/')) > 2:
            rest = path.split('/', 1)[1]
            namespaces = rest.rsplit('/', 1)[0].split('/')

        else:
            namespaces = []

        for build_job in find_build_jobs(repo_info.repo.working_dir, [collection_name], [category_name]):
            yield build_job
