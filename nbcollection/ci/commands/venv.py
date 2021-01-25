import argparse
import sys

from nbcollection.ci.constants import PROJECT_DIR
from nbcollection.ci.venv import virtual_env
from nbcollection.ci.venv.datatypes import VirtualENVType

DESCRIPTION = "Wrapper around common virtual environment utils"
EXAMPLE_USAGE = """Example Usage:

    Create virtualenv:
    nbcollection-ci install --env-type venv -d /tmp/new-notebook
"""


def convert(args=None):
    args = args or sys.argv

    parser = argparse.ArgumentParser(prog="nbcollection venv",
                                     epilog=EXAMPLE_USAGE,
                                     description=DESCRIPTION,
                                     formatter_class=argparse.RawTextHelpFormatter)
    formatted_members = ','.join([v.value for k, v in VirtualENVType.__members__.items()])
    parser.add_argument('-e', '--env-type', type=VirtualENVType, default=VirtualENVType.VirtualENV,
                        help=f'ENVTypes Available: {formatted_members}')
    parser.add_argument('-p', '--project-path', default=PROJECT_DIR, type=str,
                        help="Path relative to Project DIR install")
    parser.add_argument('-o', '--overwrite', action="store_true", default=False,
                        help="Overwrite ENV files?")

    args = parser.parse_args(args[2:])
    args.uninstall = False
    if args.env_type is VirtualENVType.VirtualENV:
        virtual_env.enable(args.project_path, args.overwrite)

    else:
        raise NotImplementedError(f'VENV-Type not supported: {args.env_type.value}')
