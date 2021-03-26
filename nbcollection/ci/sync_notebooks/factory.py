import argparse
import os
import logging
import shutil

from nbcollection.ci.scanner.utils import find_build_jobs
from nbcollection.ci.commands.utils import validate_and_parse_inputs

logger = logging.getLogger(__name__)

def run_sync_notebooks(options: argparse.Namespace) -> None:
    if not os.path.exists(options.destination_path):
        raise NotImplementedError(f'Destination Path[{options.destination_path}] does not exist')

    validate_and_parse_inputs(options)
    # https://github.com/spacetelescope/dat_pyinthesky/blob/78bfaec05eb9af6280c6d15b6df54886b1aa4e9f/.circleci/builder/factory.py#L59
    for job in find_build_jobs(options.project_path,
                               options.collection_names,
                               options.category_names,
                               options.notebook_names, True):

        notebooks_to_update = {}
        for notebook in job.category.notebooks:
            new_path = f'{options.destination_path}/{job.category.name}/{notebook.name}.ipynb'
            new_dirpath = os.path.dirname(new_path)
            source_path = f'{options.project_path}/{job.collection.name}/{job.category.name}/{notebook.name}.ipynb'
            source_dirpath = os.path.dirname(source_path)

            key = f'{job.collection.name}.{job.category.name}'
            notebooks_to_update[key] = (source_path, new_path)

        for key, (source_path, new_path) in notebooks_to_update.items():
            collection_name, category_name = key.split('.', 1)
            logger.info(f'Updating: {collection_name} - {category_name}')
            if os.path.exists(new_dirpath):
                shutil.rmtree(new_dirpath)

            shutil.copytree(source_dirpath, new_dirpath)
