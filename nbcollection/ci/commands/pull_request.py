import argparse
import sys

from nbcollection.ci.constants import PROJECT_DIR
from nbcollection.ci.pull_requests.factory import run_pull_request_build

DESCRIPTION = "Run Category builds specific to Pull Requests"
EXAMPLE_USAGE = """Example Usage:

    Replicate Github PR locally:
    nbcollection-ci pull-request --url https://github.com/spacetelescope/dat_pyinthesky/pull/111 -p /tmp/project-dir

    Source Example:
    python -m nbcollection.ci pull-request -u https://github.com/spacetelescope/dat_pyinthesky/pull/111 -p ./project-dir
"""


def convert(args=None):
    args = args or sys.argv
    parser = argparse.ArgumentParser(prog='nbcollection-ci pull-request',
                                     description=DESCRIPTION,
                                     epilog=EXAMPLE_USAGE,
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-u', '--url', help="Pull Request URL")
    parser.add_argument('-p', '--project-path', default=PROJECT_DIR, type=str,
                        help="Path relative to Project DIR install")

    args = parser.parse_args(args[2:])
    run_pull_request_build(args)
    sys.exit(0)
