import argparse
import os
import sys

from nbcollection.ci.commands.datatypes import CIMode, Site
from nbcollection.ci.constants import PROJECT_DIR
from nbcollection.ci.site_deployment.factory import run_site_deployment

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

    parser.add_argument('-b', '--publish-branch', type=str, default='gh-pages')
    parser.add_argument('-r', '--publish-remote', type=str, default='origin')
    parser.add_argument('-s', '--site', type=Site, default=Site.GithubPages)
    parser.add_argument('-d', '--site-directory', type=str, default=None)
    parser.add_argument('-p', '--project-path', default=PROJECT_DIR, type=str,
                        help="Path relative to Project DIR install")

    options = parser.parse_args(options[2:])
    if options.site_directory is None:
        options.site_directory = os.path.join(options.project_path, 'site')

    if options.publish_branch in ['main', 'master']:
        raise NotImplementedError(f'This program will not push anything to branch:{options.site_directory}')

    if options.publish_remote in ['upstream']:
        raise NotImplementedError(f'This program will not push anything to remote:{options.publish_branch}')

    run_site_deployment(options)
