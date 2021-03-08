import argparse
import sys

from nbcollection.ci.constants import PROJECT_DIR
from nbcollection.ci.commands.datatypes import CIEnvironment
from nbcollection.ci.generate_ci_environment.factory import run_generate_ci_environment

DESCRIPTION = "Build CI Configs for CircleCI, Github Actions, or others"
EXAMPLE_USAGE = """Example Usage:

    Generate .circleci/config.yaml environment
    nbcollection-ci generate-ci-env --ci-environment circle-ci

    Source Example:
    PYTHONPATH='.' python -m nbcollection.ci generate-ci-env --ci-environment circle-ci
"""


def convert(options=None):
    options = options or sys.argv

    parser = argparse.ArgumentParser(prog='nbcollection-ci generate-ci-env',
                                     description=DESCRIPTION,
                                     epilog=EXAMPLE_USAGE,
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-e', '--ci-environment', type=CIEnvironment, default=CIEnvironment.CircleCI,
                        help="Which CI Environment would you like to generate a config for?")
    parser.add_argument('-c', '--collection-names', required=False, default=None,
                        help="Select a subset of Collections to be built, or all will be built")
    parser.add_argument('-t', '--category-names', required=False, default=None,
                        help="Select a subset of Categories to be built, or all will be built")
    parser.add_argument('-n', '--notebook-names', required=False, default=None,
                        help="Select a subset of Notebooks to be built, or all will be built")
    parser.add_argument('-p', '--project-path', default=PROJECT_DIR, type=str,
                        help="Path relative to Project DIR install")
    parser.add_argument('-w', '--enable-website-publication', default=False, action='store_true',
                        help="Enable Website Publication")

    options = parser.parse_args(options[2:])
    run_generate_ci_environment(options)
