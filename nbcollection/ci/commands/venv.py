import argparse
import enum
import os
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

    parser = argparse.ArgumentParser(
            prog="nbcollection venv",
            epilog=EXAMPLE_USAGE,
            description=DESCRIPTION,
            formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-e', '--env-type', type=VirtualENVType, default=VirtualENVType.VirtualENV,
            help=f"ENVTypes Available: [{', '.join([v.value for key, v in VirtualENVType.__members__.items()])}]")
    parser.add_argument('-p', '--project-path', default=PROJECT_DIR, type=str,
            help="Path relative to Project DIR install")
    parser.add_argument('-o', '--overwrite', action="store_true", default=False,
            help="Overwrite ENV files?")

    members: typing.List[str] = VirtualENVType.__members__.values()
    args = parser.parse_args(args[2:])
    args.uninstall = False
    if args.env_type is VirtualENVType.VirtualENV:
        virtual_env.enable(args.project_path, args.overwrite)

    # elif args.env_type is VirtualENVType.VENV:
    #     enable_python_virtual_env(args.project_path)

    # elif args.env_type is VirtualENVType.Conda:
    #     enable_conda(args.project_path)

    # elif args.env_type is VirtualENVType.MiniConda:
    #     enable_miniconda(args.project_path)

    else:
        raise NotImplementedError(f'VENV-Type not supported: {args.env_type.value}')
