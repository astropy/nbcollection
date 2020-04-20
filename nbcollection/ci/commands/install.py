import argparse
import enum
import sys

from nbcollection.ci.generator import render_circle_ci
DESCRIPTION = "Install Continuous Integration"

class CIType(enum.Enum):
    CircleCI = 'circle-ci'
    GithubAcitons = 'github-actions'

def convert(args=None):
    args = args or sys.argv

    parser = argparse.ArgumentParser(description=DESCRIPTION, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-l', '--list-ci-types', action="store_true", default=False,
            help="List all CI-Types available")
    parser.add_argument('-t', '--ci-type', type=CIType, default=CIType.CircleCI,
            help="What kind of CI-Type would you like to install?")
    parser.add_argument('-r', '--repo-path', required=True,
            help="Which repo would you like to install the CI-Solution? Past a local-path, git-path, or https path")
    parser.add_argument('-o', '--overwrite', action="store_true", default=False,
            help="Overwrite CI-Solution in directory or repository")

    args = parser.parse_args(args[2:])
    args.uninstall = False
    if args.list_ci_types:
        members: str = ', '.join([ci_type.value for ci_type in CIType.__members__.values()])
        print(f'Available CI Types: {members}')
        sys.exit(0)

    members: typing.List[str] = CIType.__members__.values()
    if args.ci_type is CIType.CircleCI:
        render_circle_ci(args)

    else:
        raise NotImplementedError(f'CI-Type not supported: {args.ci_type.value}')

