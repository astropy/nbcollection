import argparse
import sys

from nbcollection.ci.constants import PROJECT_DIR
from nbcollection.ci.build_notebooks.factory import run_build
from nbcollection.ci.commands.datatypes import BuildMode


DESCRIPTION = "Build categories of notebooks"
EXAMPLE_USAGE = """Example Usage:

    Replicate Github PR locally:
    Build a Collection of Categories and Notebooks
    nbcollection-ci build-notebooks -c jdat_notebooks

    Build a category of notebooks within a collection
    nbcollection-ci build-notebooks -c jbat_notebooks -t asdf_example

    Build multiple categories of notebooks within a collection
    nbcollection-ci build-notebooks -c jbat_notebooks -t asdf_example,IFU_cube_continuum_fit

    Bulid a single notebook
    nbcollection-ci build-notebooks -c jdat_notebooks -t NIRISS_WFSS_postpipeline -n "00. Optimal extraction"

    Source Example:
    PYTHONPATH='.' python -m nbcollection.ci build-notebooks --collection-names jdat_notebooks
"""


def convert(options=None):
    options = options or sys.argv
    parser = argparse.ArgumentParser(prog='nbcollection-ci build-notebooks',
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
    parser.add_argument('-b', '--build-mode', default=BuildMode.Single, type=BuildMode,
                        help="Build in one process or many?")
    parser.add_argument('-f', '--force-build', default=False, action='store_true',
                        help="Force build excluded notebooks")

    options = parser.parse_args(options[2:])
    run_build(options)
