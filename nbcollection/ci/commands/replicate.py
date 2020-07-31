import argparse
import enum
import sys

from nbcollection.ci.generator import render_circle_ci
from nbcollection.ci.commands.datatypes import CIType

DESCRIPTION = "Replicate Notebook Environments locally"
EXAMPLE_USAGE = """Example Usage:

    Replicate Github PR locally:
    nbcollection-ci replicate --source https://github.com/spacetelescope/dat_pyinthesky/pull/111
"""

def convert(args=None):
    args = args or sys.argv

    parser = argparse.ArgumentParser(
            prog='nbcollection-ci replicate',
            description=DESCRIPTION,
            epilog=EXAMPLE_USAGE,
            formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-t', '--source', type=str, required=True, help="See Example Usage")

    args = parser.parse_args(args[2:])
    args.uninstall = False
    raise NotImplementedError

