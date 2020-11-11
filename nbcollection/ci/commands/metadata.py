import argparse
import enum
import sys

from nbcollection.ci.constants import PROJECT_DIR
from nbcollection.ci.generator import render_circle_ci
from nbcollection.ci.commands.datatypes import CIType
from nbcollection.ci.metadata.factory import run_reset_notebook_execution, run_extract_metadata

DESCRIPTION = "Extract DevNotes and other data from Jupyter Notebooks"
EXAMPLE_USAGE = """Example Usage:
    Reset Jupyter Notebook:
    nbcollection-ci metadata --mode reset-notebooks --notebook-category asdf_example --notebook-collection jdat_notebooks

    Install machinery locally:
    nbcollection-ci metadata --mode extract-metadata --notebook-category asdf_example --notebook-collection jdat_notebooks
"""

class Mode(enum.Enum):
    ResetNotebooks = 'reset-notebooks'
    ExtractMetadata = 'extract-metadata'

def convert(args=None):
    args = args or sys.argv

    parser = argparse.ArgumentParser(
            prog='nbcollection-ci metadata',
            description=DESCRIPTION,
            formatter_class=argparse.RawTextHelpFormatter,
            epilog=EXAMPLE_USAGE)
    formatted_mode_members = ','.join([mem.value for name, mem in Mode.__members__.items()])
    parser.add_argument('-m', '--mode', type=Mode, required=True,
            help="Which mode to run metadata in? \n Available Modes:[formatted_mode_members]")
    parser.add_argument('-c', '--collection-names', required=False, default=None,
            help="Select a subset of Collections to be built, or all will be built")
    parser.add_argument('-t', '--category-names', required=False, default=None, 
            help="Select a subset of Categories to be built, or all will be built")
    parser.add_argument('-n', '--notebook-names', required=False, default=None,
            help="Select a subset of Notebooks to be built, or all will be built")
    parser.add_argument('-p', '--project-path', default=PROJECT_DIR, type=str,
            help="Path relative to Project DIR install")

    args = parser.parse_args(args[2:])
    if args.mode is Mode.ResetNotebooks:
        run_reset_notebook_execution(args)

    elif args.mode is Mode.ExtractMetadata:
        run_extract_metadata(args)

    else:
        raise NotImplementedError(args.mode)

    sys.exit(0)
