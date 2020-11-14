import argparse

from nbcollection.ci.pull_requests.utils import pull_request_build

def run_pull_request_build(options: argparse.Namespace) -> None:
    if options.url is None:
        logger.info('Pull request info not found')

    pull_request_build(options.url, options.project_path)
    import pdb; pdb.set_trace()
    import sys; sys.exit(1)

# def extract_pull_request_information() -> None:
#     pull_request_url = os.environ.get('CIRCLE_PULL_REQUEST', None)
#     if pull_request_url is None:
#         return None
