from argparse import ArgumentParser
import logging

from ..logger import logger


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
            return parsed

    parser = CustomArgumentParser(description=description)

    parser.add_argument("notebooks", nargs='+',
                        help="Path to the root directory containing Jupyter "
                             "notebooks, to a single notebook file, or a list "
                             "of notebook files.")

    parser.add_argument('--build-path', default=None,
                        help='The path to save all executed or converted '
                             'notebook files. If not specified, the executed/'
                             'converted files will be in _build')

    parser.add_argument("-o", "--overwrite", action='store_true',
                        dest='overwrite',
                        help="Overwrite executed notebooks if they already "
                             "exist.")

    vq_group = parser.add_mutually_exclusive_group()
    vq_group.add_argument('-v', '--verbose', action='count', default=0,
                          dest='verbosity')
    vq_group.add_argument('-q', '--quiet', action='count', default=0,
                          dest='quietness')

    return parser
