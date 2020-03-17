import sys

from ..core import NBStaticConverter
from .argparse_helpers import get_parser

DESCRIPTION = "Convert a collection of executed Jupyter notebooks to HTML"


def convert(args=None):
    args = args or sys.argv[2:]

    parser = get_parser(DESCRIPTION)

    # Specific to this command:
    parser.add_argument("--flatten", action='store_true',
                        dest='flatten',
                        help="Flatten the directory structure of the built "
                             "notebooks. All HTML notebook files will be "
                             "written to the top-level build path.")

    args = parser.parse_args(args)

    kwargs = vars(args)

    nbstatic = NBStaticConverter(kwargs.pop('notebooks'))
    nbstatic.convert(**kwargs)
