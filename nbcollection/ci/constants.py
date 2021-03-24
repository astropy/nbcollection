import os
import typing

PWN = typing.TypeVar('PWN')
DEFAULT_BRANCH = os.environ.get('DEFAULT_BRANCH', 'main')
DEFAULT_REMOTE = os.environ.get('DEFAULT_REMOTE', 'origin')
ENCODING = 'utf-8'
PROJECT_DIR = os.getcwd()

TEMP_FOLDER = os.environ.get('TEMP_FOLDER', '/tmp')
# Scanner Module
SCANNER_BUILD_DIR = f'{TEMP_FOLDER}/nbcollection-ci/scanner-build-dir'  # nosec
SCANNER_ARTIFACT_DEST_DIR = f'{TEMP_FOLDER}/nbcollection-ci-artifacts'  # nosec
SCANNER_BUILD_LOG_DIR = f'{TEMP_FOLDER}/nbcollection-ci/scanner-build-logs'  # nosec

# Renderer Module
RENDERER_ENV_CONTEXT_PATH = os.path.join(os.getcwd(), 'env-context.toml')
RENDERER_TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'renderer/template')

# Github Auth Details
AUTH_USERNAME = os.environ.get('AUTH_USERNAME', None)
AUTH_TOKEN = os.environ.get('AUTH_TOKEN', None)

# Replicate Module
COMMIT_DATE_FORMAT = '%Y-%m-%dT%H:%M:%SZ'

# Merge Artifacts
AUTHOR_DATE_FORMAT = '%Y-%m-%dT%H:%M:%S.000Z'
CIRCLECI_TOKEN = os.environ.get('CIRCLECI_TOKEN', None)
