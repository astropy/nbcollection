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

    parser.add_argument("--index-template", dest="index_template", default=None,
                        help="A jinja2 template file used to create the index "
                             "page.")

    parser.add_argument("--make-index", dest="make_index", default=False,
                        help="Controls whether to make an index page that "
                             "lists all of the converted notebooks.")

    args = parser.parse_args(args[2:])

    kwargs = vars(args)

    nbstatic = NBStaticConverter(**kwargs)
    nbstatic.convert()
