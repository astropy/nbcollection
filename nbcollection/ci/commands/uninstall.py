import argparse
import enum
import sys

from nbcollection.ci.commands.datatypes import CIType
from nbcollection.ci.generator import render_circle_ci

DESCRIPTION = "Uninstall Astropy Jupyter notebook build machinery into a Source-Code Repository"
EXAMPLE_USAGE = """Example Usage:

    Uninstall machinery locally:
    nbcollection-ci uninstall --ci-type circle-ci --repo-path /tmp/my-new-repository

    Uninstall machinery remotely:
    nbcollection-ci uninstall --ci-type circle-ci --repo-path https://github.com/jbcurtin/notebooks
"""

def convert(args=None):
    args = args or sys.argv

    parser = argparse.ArgumentParser(
            prog='nbcollection-ci uninstall',
            epilog=EXAMPLE_USAGE,
            description=DESCRIPTION, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-t', '--ci-type', type=CIType, default=CIType.CircleCI,
            help="Supported CI-Types: [{', '.join([v.value for key, v in CIType.__members__.items()]}]")
    parser.add_argument('-r', '--repo-path', required=True,
            help="Local or remote path to repo to be uninstalled")

    args = parser.parse_args(args[2:])
    args.uninstall = True
    if args.list_ci_types:
        members: str = ', '.join([ci_type.value for ci_type in CIType.__members__.values()])
        print(f'Available CI Types: {members}')
        sys.exit(0)

    members: typing.List[str] = CIType.__members__.values()
    if args.ci_type is CIType.CircleCI:
        render_circle_ci(args)

    else:
        raise NotImplementedError(f'CI-Type not supported: {args.ci_type.value}')

