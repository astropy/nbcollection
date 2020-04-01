import sys
from nbconvert.exporters import HTMLExporter
from .argparse_helpers import (get_parser, get_converter,
                               _trait_type_map, convert_trait_names)

DESCRIPTION = "Convert a collection of Jupyter notebooks to HTML"


def convert(args=None):
    args = args or sys.argv

    parser = get_parser(DESCRIPTION)

    # Specific to this command:
    parser.add_argument("--index-template", dest="index_template",
                        default=None, type=str,
                        help="A jinja2 template file used to create the index "
                             "page.")

    parser.add_argument("--make-index", dest="make_index", default=False,
                        help="Controls whether to make an index page that "
                             "lists all of the converted notebooks.")

    for trait_name in convert_trait_names:
        trait = getattr(HTMLExporter, trait_name)
        parser.add_argument("--" + trait_name.replace('_', '-'),
                            default=trait.default_value,
                            type=_trait_type_map[type(trait)],
                            help=trait.help)

    args = parser.parse_args(args[2:])
    nbstatic = get_converter(args)
    # nbstatic.convert()
