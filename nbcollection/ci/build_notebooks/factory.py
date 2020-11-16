import argparse
import logging
import os

from nbcollection.ci.commands.utils import validate_and_parse_inputs
from nbcollection.ci.scanner.utils import find_build_jobs, generate_job_context, run_job_context

logger = logging.getLogger(__name__)
def run_build(options: argparse.ArgumentParser) -> None:
    # If CI_PULL_REQUEST exists, its probably a pull request and we don't want to run builds for all categories/notebooks
    if not os.environ.get('CI_PULL_REQUEST', None) is None:
        logger.info(f'Pull Request detected. Skipping Build')
        return None

    validate_and_parse_inputs(options)
    for job_idx, job in enumerate(find_build_jobs(
                                    options.project_path,
                                    options.collection_names,
                                    options.category_names,
                                    options.notebook_names)):
        job_context = generate_job_context(job)
        run_job_context(job_context, True)
