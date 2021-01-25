import argparse
import git
import logging
import os

from nbcollection.ci.replicate.utils import find_repo_path_by_remote, obtain_pull_request_info, \
        select_build_jobs, extract_repo_info
from nbcollection.ci.replicate.datatypes import RemoteParts
from nbcollection.ci.generator.datatypes import select_repo_type, select_url_type, URLType
from nbcollection.ci.venv import virtual_env

logger = logging.getLogger(__name__)


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
            obtain_pull_request_info(url_parts)

        url_parts_ref = f'{url_parts.org}/{url_parts.repo_name}'
        logger.info(f'Loading Pull Request [{url_parts.pull_request_number}] info for {url_parts_ref} in {repo_path}')
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

            repo_info = extract_repo_info(repo, pr_info)

    else:
        raise NotImplementedError(url_parts.url_type)

    for idx, build_job in enumerate(select_build_jobs(repo_info, pr_info)):
        if idx > 0:
            raise NotImplementedError

        virtual_env.enable(build_job, repo_info, pr_info)
