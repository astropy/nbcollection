import argparse
import sys

from nbcollection.ci.generator import render_circle_ci
from nbcollection.ci.commands.datatypes import CIType

DESCRIPTION = "Install Astropy Jupyter notebook build machinery into a Source-Code Repository"
EXAMPLE_USAGE = """Example Usage:

    Install machinery locally:
    nbcollection-ci install --ci-type circle-ci --repo-path /tmp/my-new-repository

    Install build machinery remotely:
    nbcollection-ci install --ci-type circle-ci --repo-path https://github.com/jbcurtin/notebooks
"""


def convert(args=None):
    args = args or sys.argv
    parser = argparse.ArgumentParser(prog='nbcollection-ci install',
                                     description=DESCRIPTION,
                                     formatter_class=argparse.RawTextHelpFormatter,
                                     epilog=EXAMPLE_USAGE)
    parser.add_argument('-t', '--ci-type', type=CIType, required=True,
                        help=f"Supported CI-Types: [{', '.join([v.value for key, v in CIType.__members__.items()])}]")
    parser.add_argument('-r', '--repo-path', required=True,
                        help="Local or remote path to repo to be installed")
    parser.add_argument('-o', '--overwrite', action="store_true", default=False,
                        help="Overwrite CI-Solution in local or remote path")

    args = parser.parse_args(args[2:])
    args.uninstall = False
    if args.ci_type is CIType.CircleCI:
        render_circle_ci(args)

    else:
        raise NotImplementedError(f'CI-Type not supported: {args.ci_type.value}')
