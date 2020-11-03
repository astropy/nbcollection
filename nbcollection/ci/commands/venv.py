import argparse
import enum
import os
import sys

from nbcollection.ci.commands.datatypes import VirtualENVType
# from nbcollection.ci.venv import \
#         enable_virtual_env, \
#         enable_python_virtual_env, \
#         enable_conda, \
#         enable_miniconda

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
    parser.add_argument('-e', '--env-type', type=VirtualENVType, default=VirtualENVType.VENV,
            help=f"ENVTypes Available: [{', '.join([v.value for key, v in VirtualENVType.__members__.items()])}]")
    parser.add_argument('-d', '--directory', default=os.getcwd(),
            help="Which directory would you like to install")
    parser.add_argument('-o', '--overwrite', action="store_true", default=False,
            help="Overwrite ENV files?")

    members: typing.List[str] = VirtualENVType.__members__.values()
    args = parser.parse_args(args[2:])
    args.uninstall = False
    if args.env_type is VirtualENVType.VirtualENV:
        enable_virtual_env(args)

    elif args.env_type is VirtualENVType.VENV:
        enable_python_virtual_env(args)

    elif args.env_type is VirtualENVType.Conda:
        enable_conda(args)

    elif args.env_type is VirtualENVType.MiniConda:
        enable_miniconda(args)

    else:
        raise NotImplementedError(f'VENV-Type not supported: {args.ci_type.value}')
