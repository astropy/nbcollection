import argparse
import logging

from nbcollection.ci.pull_requests.utils import pull_request_build

logger = logging.getLogger(__name__)

def run_pull_request_build(options: argparse.Namespace) -> None:
    if options.url is None:
        logger.info(f'Pull Request not detected. Skipping Build')
        return None

    pull_request_build(options.url, options.project_path)
