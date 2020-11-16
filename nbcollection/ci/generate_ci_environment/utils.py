import copy
import logging
import os
import typing
import yaml

from nbcollection.ci.constants import ENCODING, SCANNER_ARTIFACT_DEST_DIR
from nbcollection.ci.generate_ci_environment.constants import NBCOLLECTION_BUILDER, CONFIG_TEMPLATE, JOB_TEMPLATE
from nbcollection.ci.commands.datatypes import CIEnvironment
from nbcollection.ci.datatypes import BuildJob

logger = logging.getLogger(__name__)

def gen_ci_env(jobs: typing.List[BuildJob], ci_env: CIEnvironment, project_path: str) -> None:
    if not ci_env is CIEnvironment.CircleCI:
        raise NotImplementedError(f'CIEnvironment "{ci_env}" not supported')

    config = copy.deepcopy(CONFIG_TEMPLATE)
    logger.info(f'Using {NBCOLLECTION_BUILDER} for CircleCI Image Executor')
    for build_job in jobs:
        formatted_cat_name = ' '.join(build_job.category.name.split('_'))
        formatted_cat_name = formatted_cat_name.title()
        formatted_col_name = ' '.join(build_job.collection.name.split('_'))
        formatted_col_name = formatted_col_name.title()

        job_name = '-'.join([formatted_col_name, formatted_cat_name])
        logger.info(f'Generating job for "{job_name}"')
        job = copy.deepcopy(JOB_TEMPLATE)
        job['steps'][1]['run']['command'] = f'nbcollection-ci build-notebooks --collection-names {build_job.collection.name} --category-names {build_job.category.name}'
        job['steps'][1]['run']['name'] = f'Build {job_name} notebooks'
        job['steps'][2]['store_artifacts']['path'] = SCANNER_ARTIFACT_DEST_DIR

        config['jobs'][job_name] = job
        config['workflows']['Build']['jobs'].append(job_name)

    config_path = os.path.join(project_path, '.circleci/config.yml')
    config_dirpath = os.path.dirname(config_path)
    if not os.path.exists(config_dirpath):
        os.makedirs(config_dirpath)

    logger.info(f'Writing config-file to "{config_path}"')
    with open(config_path, 'wb') as stream:
        stream.write(yaml.dump(config).encode(ENCODING))
