import argparse
import enum
import sys

from nbcollection.ci.generator import render_circle_ci
from nbcollection.ci.commands.datatypes import CIType
from nbcollection.ci.metadata import extract_metadata

DESCRIPTION = "Extract DevNotes and other data from Jupyter Notebooks"
EXAMPLE_USAGE = """Example Usage:

    Install machinery locally:
    nbcollection-ci metadata --notebook-category asdf_example --notebook-collection jdat_notebooks --output stdout --output-path None
"""

def convert(args=None):
    args = args or sys.argv

    parser = argparse.ArgumentParser(
            prog='nbcollection-ci metadata',
            description=DESCRIPTION,
            formatter_class=argparse.RawTextHelpFormatter,
            epilog=EXAMPLE_USAGE)
    parser.add_argument('-n', '--notebook-category', required=True,
            help="Notebook Category to extract DevNotes and other Metadata frome")
    parser.add_argument('-l', '--notebook-collection', required=True,
            help="Notebook Collection which will contain a respective Notebook Category")
    parser.add_argument('-o', '--output', type=Output, default=Output.STDOUT,
            help="Where to pipe the output file")
    parser.add_argument('-p', '--output-dir', type=str, default=None)

    args = parser.parse_args(args[2:])
    extract_metadata(args)
    sys.exit(0)
