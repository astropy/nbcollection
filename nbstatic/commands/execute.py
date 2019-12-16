import sys

from ..core import NBStaticConverter
from .argparse_helpers import get_parser

DESCRIPTION = "Execute a collection of Jupyter notebooks"


def execute():
    parser = get_parser(DESCRIPTION)

    # Specific to this command:
    parser.add_argument("--kernel-name", default='python3', type=str,
                        help="The name of an IPython kernel to run the "
                             "notebooks with.")
    parser.add_argument("--timeout", default=None, type=int,
                        help="The timeout (in seconds) for executing notebooks")

    args = parser.parse_args(sys.argv[2:])

    kwargs = vars(args)

    nbstatic = NBStaticConverter(kwargs.pop('nb_root_path'))
    nbstatic.execute(overwrite=args.overwrite,
                     **kwargs)
