import sys

from ..core import NBStaticConverter
from .argparse_helpers import get_parser

DESCRIPTION = "Execute a collection of Jupyter notebooks"


def execute(args=None):
    args = args or sys.argv

    parser = get_parser(DESCRIPTION)

    # Specific to this command:
    parser.add_argument("--kernel-name", default='python3', type=str,
                        help="The name of an IPython kernel to run the "
                             "notebooks with.")
    parser.add_argument("--timeout", default=None, type=int,
                        help="The timeout (in seconds) for executing notebooks")
    parser.add_argument("--stop-on-error", action='store_true', default=False,
                        help="The timeout (in seconds) for executing notebooks")

    args = parser.parse_args(args[2:])

    kwargs = vars(args)

    nbstatic = NBStaticConverter(**kwargs)
    nbstatic.execute(kwargs.get('stop_on_error', False))
