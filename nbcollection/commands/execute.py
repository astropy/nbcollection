import sys
from nbconvert.preprocessors import ExecutePreprocessor
from .argparse_helpers import (get_parser, get_converter,
                               _trait_type_map, execute_trait_names)

DESCRIPTION = "Execute a collection of Jupyter notebooks"


def execute(args=None):
    args = args or sys.argv

    parser = get_parser(DESCRIPTION)

    # Specific to this command:
    for trait_name in execute_trait_names:
        trait = getattr(ExecutePreprocessor, trait_name)
        parser.add_argument("--" + trait_name.replace('_', '-'),
                            default=trait.default_value,
                            type=_trait_type_map[type(trait)],
                            help=trait.help)

    args = parser.parse_args(args[2:])
    nbcollection = get_converter(args)
    nbcollection.execute()
