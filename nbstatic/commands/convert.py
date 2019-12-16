import sys

from ..core import NBStaticConverter
from .argparse_helpers import get_parser

DESCRIPTION = "Convert a collection of executed Jupyter notebooks to HTML"


def convert():
    parser = get_parser(DESCRIPTION)

    # Specific to this command:

    args = parser.parse_args(sys.argv[2:])

    kwargs = vars(args)

    nbstatic = NBStaticConverter(kwargs.pop('nb_root_path'))
    nbstatic.convert(**kwargs)
