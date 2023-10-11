"""The nbcollection convert command."""

import sys

from nbconvert.exporters import HTMLExporter

from .argparse_helpers import (
    _trait_type_map,
    convert_trait_names,
    get_converter,
    get_parser,
)

DESCRIPTION = "Convert a collection of Jupyter notebooks to HTML"


def convert(args=None):
    """Run the convert command."""
    args = args or sys.argv

    parser = get_parser(DESCRIPTION)

    # Specific to this command:
    parser.add_argument(
        "--index-template",
        dest="index_template",
        default=None,
        type=str,
        help="A jinja2 template file used to create the index page.",
    )

    parser.add_argument(
        "--make-index",
        dest="make_index",
        default=False,
        action="store_true",
        help="Controls whether to make an index page that "
        "lists all of the converted notebooks.",
    )

    parser.add_argument(
        "--preprocessors",
        nargs="*",
        default=[],
        help="Preprocessors for convert. For example, "
        "nbconvert.preprocessors.ExtractOutputPreprocessor",
    )

    for trait_name in convert_trait_names:
        trait = getattr(HTMLExporter, trait_name)
        parser.add_argument(
            "--" + trait_name.replace("_", "-"),
            default=trait.default_value,
            type=_trait_type_map[type(trait)],
            help=trait.help,
        )

    args = parser.parse_args(args[2:])
    nbcollection = get_converter(args)
    nbcollection.convert()

    if args.make_index:
        nbcollection.make_html_index(args.index_template)
