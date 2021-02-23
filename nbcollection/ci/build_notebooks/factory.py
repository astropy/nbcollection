import argparse
import logging
import os

from nbcollection.ci.commands.utils import validate_and_parse_inputs
from nbcollection.ci.commands.datatypes import BuildMode
from nbcollection.ci.scanner.utils import find_build_jobs, generate_job_context, run_job_context
from nbcollection.ci.build_notebooks.multi import build_artifacts_concurrently

logger = logging.getLogger(__name__)


def run_build(options: argparse.ArgumentParser) -> None:
    if not os.environ.get('CI_PULL_REQUEST', None) is None:
        logger.info('Pull Request detected. Skipping Build')
        return None

    validate_and_parse_inputs(options)

    # Find Builds
    jobs = []
    for job in find_build_jobs(options.project_path,
                               options.collection_names,
                               options.category_names,
                               options.notebook_names):
        jobs.append(job)

    # Run Build
    artifact_paths = {}
    if options.build_mode is BuildMode.Single:
        job_context = generate_job_context(job)
        run_job_context(job_context, True)
        for notebook in job_context.notebooks:
            hash_name = f'{notebook.collection_name}-{notebook.category_name}'
            artifact_paths[hash_name] = notebook.artifact.path

    else:
        build_artifacts_concurrently(options, jobs, artifact_paths)

    for name, path in artifact_paths.items():
        logger.info(f'Artifact[{name}] created here: {path}')
