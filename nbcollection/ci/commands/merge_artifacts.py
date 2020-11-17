import argparse
import sys

from nbcollection.ci.constants import PROJECT_DIR
from nbcollection.ci.merge_artifacts.factory import run_merge_artifacts

DESCRIPTION = "Build CI Configs for CircleCI, Github Actions, or others"
EXAMPLE_USAGE = """Example Usage:

    Generate .circleci/config.yaml environment
    nbcollection-ci merge-artifacts --collection-names jdat_notebooks

    Source Example:
    PYTHONPATH='.' python -m nbcollection.ci merge-artifacts --collection-names jdat_notebooks
"""

def convert(options=None):
    options = options or sys.argv

    parser = argparse.ArgumentParser(
            prog='nbcollection-ci merge-artifacts',
            description=DESCRIPTION,
            epilog=EXAMPLE_USAGE,
            formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-c', '--collection-names', required=False, default=None,
            help="Select a subset of Collections to be built, or all will be built")
    parser.add_argument('-t', '--category-names', required=False, default=None,
            help="Select a subset of Categories to be built, or all will be built")
    parser.add_argument('-n', '--notebook-names', required=False, default=None,
            help="Select a subset of Notebooks to be built, or all will be built")
    parser.add_argument('-p', '--project-path', default=PROJECT_DIR, type=str,
            help="Path relative to Project DIR install")
    parser.add_argument('-r', '--repo-name', required=True, type=str,
            help="Which CI Project should be merged?")
    parser.add_argument('-o', '--org', required=True, type=str,
            help="Which org runs the CI Project?")

    options = parser.parse_args(options[2:])
    run_merge_artifacts(options)
