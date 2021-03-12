import argparse
import os

from nbcollection.ci.scanner.utils import find_build_jobs

def run_sync_notebooks(options: argparse.Namespace) -> None:
    if not os.path.exists(options.destination_path):
        raise NotImplementedError(f'Destination Path[{options.destination_path}] does not exist')

    # https://github.com/spacetelescope/dat_pyinthesky/blob/78bfaec05eb9af6280c6d15b6df54886b1aa4e9f/.circleci/builder/factory.py#L59
    for job in find_build_jobs(options.project_path,
                               options.collection_names,
                               options.category_names,
                               options.notebook_names):
        raise NotImplementedError
