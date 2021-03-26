import argparse
import sys

from nbcollection.ci.constants import PROJECT_DIR
from nbcollection.ci.sync_notebooks.factory import run_sync_notebooks

DESCRIPTION = "Sync Notebooks between two folders"
EXAMPLE_USAGE = """
Sync Notebooks copies notebook categories into another space in the file-system

nbcollection-ci sync-notebooks -c jdat_notebooks -d ../jdat_notebooks/notebooks

Source Example
PYTHONPATH='.' python -m nbcollection.ci sync-notebooks -c jdat_notebooks -d ../jdat_notebooks/notebooks
"""


def convert(options=None):
    options = options or sys.argv

    parser = argparse.ArgumentParser(
            prog='nbcollection-ci merge-artifacts',
            description=DESCRIPTION,
            epilog=EXAMPLE_USAGE,
            formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('-c', '--collection-names', required=False, default=None,
                        help="Select a subset of Collections to be built, or all will be built")
    parser.add_argument('-t', '--category-names', required=False, default=None,
                        help="Select a subset of Categories to be built, or all will be built")
    parser.add_argument('-n', '--notebook-names', required=False, default=None,
                        help="Select a subset of Notebooks to be built, or all will be built")
    parser.add_argument('-p', '--project-path', default=PROJECT_DIR, type=str,
                        help="Path relative to Project DIR install")
    parser.add_argument('-d', '--destination-path', type=str, required=True)

    options = parser.parse_args(options[2:])
    run_sync_notebooks(options)
