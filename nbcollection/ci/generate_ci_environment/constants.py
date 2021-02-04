NBCOLLECTION_BUILDER = 'jbcurtin/nbcollection-builder'
NBCOLLECTION_BUILDER_CIRCLE_CI_TIMEOUT = '60m'
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
                'no_output_timeout': NBCOLLECTION_BUILDER_CIRCLE_CI_TIMEOUT,
            },
        },
        {
            'store_artifacts': {
                'path': '/tmp/nbcollection-ci-artifacts',  # nosec
            }
        }
    ]
}
PULL_REQUEST_TEMPLATE = {
    'executor': 'nbcollection-builder',
    'steps': [
        'checkout',
        {
            'run': {
                'no_output_timeout': NBCOLLECTION_BUILDER_CIRCLE_CI_TIMEOUT,
                'command': 'nbcollection-ci pull-request -u $CI_PULL_REQUEST',
                'name': 'Build Pull Request',
            },
        },
        {
            'store_artifacts': {
                'path': '/tmp/nbcollection-ci-artifacts',  # nosec
            }
        }
    ]
}
