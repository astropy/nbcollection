import sys

from ..core import NBStaticConverter
from .argparse_helpers import get_parser

DESCRIPTION = "Convert a collection of executed Jupyter notebooks to HTML"


def convert(args=None):
    args = args or sys.argv

    parser = get_parser(DESCRIPTION)

    # Specific to this command:
    parser.add_argument("--template", dest="template", default=None,
                        help="A jinja2 template file passed to nbconvert.")

    args = parser.parse_args(args[2:])

    kwargs = vars(args)

    nbstatic = NBStaticConverter(**kwargs)
    nbstatic.execute()
    nbstatic.convert()
