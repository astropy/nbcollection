import os
import typing

PWN = typing.TypeVar('PWN')
DEFAULT_BRANCH = os.environ.get('DEFAULT_BRANCH', 'main')
DEFAULT_REMOTE = os.environ.get('DEFAULT_REMOTE', 'origin')
ENCODING = 'utf-8'
PROJECT_DIR = os.getcwd()

# Scanner Module
SCANNER_BUILD_DIR = '/tmp/nbcollection-ci/scanner-build-dir'
SCANNER_ARTIFACT_DEST_DIR = '/tmp/nbcollection-ci-artifacts'
SCANNER_BUILD_LOG_DIR = '/tmp/nbcollection-ci/scanner-build-logs'

# Renderer Module
RENDERER_ENV_CONTEXT_PATH = os.path.join(os.getcwd(), 'env-context.toml')
RENDERER_TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'renderer/template')

# Github Auth Details
GITHUB_USERNAME = os.environ.get('GITHUB_USERNAME', None)
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN', None)

# Replicate Module
COMMIT_DATE_FORMAT = '%Y-%m-%dT%H:%M:%SZ'
