import argparse
import enum
import os
import sys

from nbcollection.ci.constants import PROJECT_DIR
from nbcollection.ci.generator import render_circle_ci
from nbcollection.ci.commands.datatypes import CIType
from nbcollection.ci.replicate import run_replication


DESCRIPTION = "Replicate Notebook Environments locally"
EXAMPLE_USAGE = """Example Usage:

    Replicate Github PR locally:
    nbcollection-ci replicate --repo-path https://github.com/spacetelescope/dat_pyinthesky/pull/111 /tmp/
"""

def convert(args=None):
    args = args or sys.argv

    parser = argparse.ArgumentParser(
            prog='nbcollection-ci replicate',
            description=DESCRIPTION,
            epilog=EXAMPLE_USAGE,
            formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-r', '--repo-path', required=True,
            help="Local or remote path to repo to be replicated")
    parser.add_argument('-p', '--project-path', default=PROJECT_DIR, type=str,
            help="Path relative to Project DIR install")

    args = parser.parse_args(args[2:])
    run_replication(args)
