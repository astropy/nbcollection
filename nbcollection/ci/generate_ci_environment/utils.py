import copy
import logging
import os
import typing
import yaml

from nbcollection.ci.constants import ENCODING, SCANNER_ARTIFACT_DEST_DIR
from nbcollection.ci.generate_ci_environment.constants import NBCOLLECTION_BUILDER, CONFIG_TEMPLATE, JOB_TEMPLATE, \
        PULL_REQUEST_TEMPLATE, NBCOLLECTION_WORKFLOW_NAME, PUBLISH_JOB_NAME_TEMPLATE
from nbcollection.ci.commands.datatypes import CIEnvironment
from nbcollection.ci.datatypes import BuildJob
from nbcollection.ci.renderer import render_template

logger = logging.getLogger(__name__)


def gen_ci_env(jobs: typing.List[BuildJob], ci_env: CIEnvironment, project_path: str, enable_website_publication: bool) -> None:
    if ci_env is not CIEnvironment.CircleCI:
        raise NotImplementedError(f'CIEnvironment "{ci_env}" not supported')

    formatted_collections = []
    formatted_job_names = []
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
        job['steps'][2]['run']['command'] = ' '.join([
            'nbcollection-ci build-notebooks',
            f'--collection-names {build_job.collection.name}',
            f'--category-names {build_job.category.name}',
        ])
        job['steps'][2]['run']['name'] = f'Build {job_name} notebooks'
        job['steps'][3]['store_artifacts']['path'] = SCANNER_ARTIFACT_DEST_DIR

        config['jobs'][job_name] = job
        config['workflows'][NBCOLLECTION_WORKFLOW_NAME]['jobs'].append(job_name)
        if not build_job.collection.name in formatted_collections:
            formatted_collections.append(build_job.collection.name)

        formatted_job_names.append(job_name)

    formatted_collections = ','.join(formatted_collections)

    # Pull Request
    pr_job_name = 'Pull Request'
    config['jobs'][pr_job_name] = copy.deepcopy(PULL_REQUEST_TEMPLATE)
    config['workflows'][NBCOLLECTION_WORKFLOW_NAME]['jobs'].append(pr_job_name)

    # Publish Website
    if enable_website_publication:
        publish_job_name = 'Publish Website'
        config['jobs'][publish_job_name] = copy.deepcopy(PUBLISH_JOB_NAME_TEMPLATE)
        config['jobs'][publish_job_name]['steps'][1]['run']['command'] = f'nbcollection-ci merge-artifacts -c {formatted_collections}'
        config['jobs'][publish_job_name]['steps'][1]['run']['name'] = 'Publish Website'
        config['workflows'][NBCOLLECTION_WORKFLOW_NAME]['jobs'].append({
            publish_job_name: {
                'requires': formatted_job_names
            }
        })

    config_path = os.path.join(project_path, '.circleci/config.yml')
    config_dirpath = os.path.dirname(config_path)
    if not os.path.exists(config_dirpath):
        os.makedirs(config_dirpath)

    logger.info(f'Writing config-file to "{config_path}"')
    with open(config_path, 'wb') as stream:
        stream.write(yaml.dump(config).encode(ENCODING))

    setup_script_filepath = os.path.join(project_path, '.circleci/setup-env.sh')
    logger.info(f"Rendering Setup Script: {setup_script_filepath}")
    with open(setup_script_filepath, 'wb') as stream:
        rendered_script = render_template('setup-env.sh', {})
        stream.write(rendered_script.encode(ENCODING))
