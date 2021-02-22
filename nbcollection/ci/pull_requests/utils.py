import git
import os
import typing

from nbcollection.ci.replicate.utils import obtain_pull_request_info, select_build_jobs_by_pr_author_commits, \
        extract_repo_info
from nbcollection.ci.replicate.datatypes import RemoteParts, select_repo_type, select_url_type, URLType
from nbcollection.ci.scanner.utils import generate_job_context, run_job_context, find_build_jobs


def pull_request_build(
        url: str,
        project_path: str,
        collection_names: typing.List[str] = [],
        category_names: typing.List[str] = []) -> None:
    repo_path, repo_type = select_repo_type(url)
    url_parts = select_url_type(url, repo_type)
    if url_parts.url_type is URLType.GithubPullRequest:
        repo_path = project_path
        if not os.path.exists(repo_path):
            git.Repo.clone_from(url_parts.https_url, repo_path)

        repo = git.Repo(repo_path)
        RemoteParts.ParseURLToRemoteParts(repo.remotes.origin.url)
        pr_info = obtain_pull_request_info(url_parts)
        if getattr(repo.remotes, pr_info.source.org, None) is None:
            repo.create_remote(pr_info.source.org, pr_info.source.https_url)

        repo_info = extract_repo_info(repo, pr_info)
        build_jobs = {}

        # This automation exists to make it easier to run dynamic PRs. Rather than expecting the Scientist to install
        #   the build machinery per notebook-category. We'll have the categories detected via commits created in the
        #   PullRequest

        # The automation can be bypassed by the Scientist nistalling the build machinery with specific notebook-category
        #   specifications
        if len(collection_names) > 0:
            for job in select_build_jobs_by_pr_author_commits(repo_info, pr_info):
                if not job.semantic_path() in build_jobs.keys():
                    build_jobs[job.semantic_path()] = job
        else:
            for job in find_build_jobs(repo_info.repo.working_dir, collection_names, category_names):
                build_jobs[job.semantic_path()] = job

        for semantic_path, build_job in build_jobs.items():
            job_context = generate_job_context(job)
            run_job_context(job_context, True)

    else:
        raise NotImplementedError(f'Unable to parse URL[{url}]')
