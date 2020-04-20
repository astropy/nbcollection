import argparse
import enum
import os
import sys

from nbcollection.ci.venv import enable_virtual_env
DESCRIPTION = "Install Continuous Integration"

class VirtualENVType(enum.Enum):
    # https://docs.python.org/3/library/venv.html
    VENV = 'python-venv'
    # https://virtualenv.pypa.io/en/latest/user_guide.html
    VirtualENV = 'virtualenv'
    # https://docs.conda.io/projects/conda/en/latest/api/index.html
    Conda = 'conda'
    # https://docs.conda.io/en/latest/miniconda.html
    MiniConda = 'mini-conda'

def convert(args=None):
    args = args or sys.argv

    parser = argparse.ArgumentParser(description=DESCRIPTION, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-l', '--list-env-types', action="store_true", default=False,
            help="List all ENV Types")
    parser.add_argument('-e', '--env-type', type=VirtualENVType, default=VirtualENVType.VENV,
            help="Which ENV Type would you like to use+")
    parser.add_argument('-d', '--directory', default=os.getcwd(),
            help="Which directory would you like to install")
    parser.add_argument('-o', '--overwrite', action="store_true", default=False,
            help="Overwrite ENV files?")
    parser.add_argument('-u', '--uninstall', action="store_true", default=False,
            help="Uninstall ENV files?")

    args = parser.parse_args(args[2:])
    if args.list_env_types:
        members: str = ', '.join([ve_type.value for ve_type in VirtualENVType.__members__.values()])
        print(f'Available Virtual ENV Types: {members}')
        sys.exit(0)

    members: typing.List[str] = VirtualENVType.__members__.values()
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

