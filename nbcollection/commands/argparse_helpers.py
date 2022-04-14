from argparse import ArgumentParser
import logging
import sys

import traitlets

from ..logger import logger
from nbcollection import nbcollectionConverter


_trait_type_map = {
    traitlets.Unicode: str,
    traitlets.Int: int,
    traitlets.Bool: bool
}

execute_trait_names = ['kernel_name', 'timeout', 'allow_errors']
convert_trait_names = ['template_file', ]  # TODO: add exclude_*?


def set_log_level(args, logger):

    if args.verbosity == 1:
        log_level = logging.DEBUG

    elif args.verbosity == 2:
        log_level = 1

    elif args.verbosity == 3:
        log_level = 0

    elif args.quietness == 1:
        log_level = logging.WARNING

    elif args.quietness == 2:
        log_level = logging.ERROR

    else:
        log_level = logging.INFO  # default

    logger.setLevel(log_level)


def get_parser(description):

    class CustomArgumentParser(ArgumentParser):

        def parse_args(self, *args, **kwargs):
            parsed = super().parse_args(*args, **kwargs)
            set_log_level(parsed, logger)

            if parsed.notebooks is None:
                if not sys.stdin.isatty():
                    stdin = sys.stdin.read().strip()
                    parsed.notebooks = stdin.split()

            return parsed

    parser = CustomArgumentParser(description=description)

    parser.add_argument("notebooks", nargs='*', default=None,
                        help="Path to the root directory containing Jupyter "
                             "notebooks, to a single notebook file, or a "
                             "list of notebook files.")

    parser.add_argument('--build-path', dest='build_path',
                        help='The path to save all executed or converted '
                             'notebook files. If not specified, the executed/'
                             'converted files will be in _build')

    parser.add_argument("--flatten", action='store_true',
                        dest='flatten', default=False,
                        help="Flatten the directory structure of the built "
                             "notebooks. All HTML notebook files will be "
                             "written to the top-level build path.")

    parser.add_argument("-o", "--overwrite", action='store_true',
                        dest='overwrite',
                        help="Overwrite executed notebooks if they already "
                             "exist.")

    parser.add_argument('--exclude', dest='exclude_pattern',
                        help='A regular expression to match against files in '
                             'the target path, used to exclude files')

    parser.add_argument('--include', dest='include_pattern',
                        help='A regular expression to match against files in '
                             'the target path, used to include files')

    vq_group = parser.add_mutually_exclusive_group()
    vq_group.add_argument('-v', '--verbose', action='count', default=0,
                          dest='verbosity')
    vq_group.add_argument('-q', '--quiet', action='count', default=0,
                          dest='quietness')

    return parser


def get_converter(args):
    kw = {}

    execute_kw = {}
    for k in execute_trait_names:
        if hasattr(args, k):
            execute_kw[k] = getattr(args, k)

    convert_kw = {}
    for k in convert_trait_names:
        if hasattr(args, k):
            convert_kw[k] = getattr(args, k)

    kw['execute_kwargs'] = execute_kw
    kw['convert_kwargs'] = convert_kw

    # Bit of a hack, but it seems like explicitly passing a value for
    # template_file (even if it is the default, null value) raises an error in
    # nbconvert
    kw['convert_kwargs'].pop('template_file', None)

    if hasattr(args, 'preprocessors'):
        kw['convert_preprocessors'] = args.preprocessors

    # Process the other flags:
    kwargs = vars(args)
    for k in kwargs:
        if k in list(execute_kw.keys()) + list(convert_kw.keys()):
            continue
        kw[k] = getattr(args, k)

    print(kw)
    return nbcollectionConverter(**kw)
