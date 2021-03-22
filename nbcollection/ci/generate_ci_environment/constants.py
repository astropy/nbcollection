from nbcollection.ci.constants import SCANNER_ARTIFACT_DEST_DIR

NBCOLLECTION_BUILDER = 'continuumio/miniconda3:latest'
NBCOLLECTION_BUILDER_CIRCLE_CI_TIMEOUT = '120m'
NBCOLLECTION_WORKFLOW_NAME = 'Build Notebooks'


CONFIG_TEMPLATE = {
    'version': 2.1,
    'executors': {
        'nbcollection-builder': {
            'docker': [{'image': NBCOLLECTION_BUILDER}],
            'resource_class': 'medium',
            'working_directory': '~/repo',
        }
    },
    'jobs': {},
    'workflows': {
        'version': '2.1',
        NBCOLLECTION_WORKFLOW_NAME: {
            'jobs': []
        }
    }
}
JOB_TEMPLATE = {
    'executor': 'nbcollection-builder',
    'steps': [
        'checkout',
        {
            'run': {
                'command': 'bash ./.circleci/setup-env.sh',
                'name': 'Setup Environment',
            },
        },
        {
            'run': {
                'no_output_timeout': NBCOLLECTION_BUILDER_CIRCLE_CI_TIMEOUT,
            },
        },
        {
            'store_artifacts': {
                'path': SCANNER_ARTIFACT_DEST_DIR,
            },
        },
    ]
}
PULL_REQUEST_TEMPLATE = {
    'executor': 'nbcollection-builder',
    'steps': [
        'checkout',
        {
            'run': {
                'command': 'bash ./.circleci/setup-env.sh',
                'name': 'Setup Environment',
            },
        },
        {
            'run': {
                'no_output_timeout': NBCOLLECTION_BUILDER_CIRCLE_CI_TIMEOUT,
                'command': 'bash ./.circleci/build-pull-request.sh',
                'name': 'Build Pull Request',
            },
        },
        {
            'store_artifacts': {
                'path': SCANNER_ARTIFACT_DEST_DIR,
            }
        }
    ]
}
PUBLISH_JOB_NAME_TEMPLATE = {
    'executor': 'nbcollection-builder',
    'steps': [
        'checkout',
        {
            'run': {
                'command': 'bash ./.circleci/setup-env.sh',
                'name': 'Setup Environment',
                'no_output_timeout': NBCOLLECTION_BUILDER_CIRCLE_CI_TIMEOUT,
            },
        },
        {
            'run': {
                'no_output_timeout': NBCOLLECTION_BUILDER_CIRCLE_CI_TIMEOUT,
            },
        },
        'add_ssh_keys',
        {
            'run': {
                'name': 'Deploy Website',
                'command': 'nbcollection-ci site-deployment -r origin -b gh-pages',
                'no_output_timeout': NBCOLLECTION_BUILDER_CIRCLE_CI_TIMEOUT,
            }
        },
    ]
}
