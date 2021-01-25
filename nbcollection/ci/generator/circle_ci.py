import logging
import os
import shutil
import typing

from jinja2.environment import Template

from nbcollection.ci import exceptions as ci_exceptions
from nbcollection.ci.template import ENVIRONMENT
from nbcollection.ci.generator import datatypes as generator_datatypes

CI_DIRECTORY: str = '.circleci'
PWN: typing.TypeVar = typing.TypeVar('PWN')
logger = logging.getLogger(__name__)


class CircleCiRepo(generator_datatypes.Repo):
    _ci_directory_path: str

    def __init__(self: PWN, *args, **kwargs) -> None:
        super(CircleCiRepo, self).__init__(*args, **kwargs)
        self._ci_directory_path = os.path.join(self.repo_path, CI_DIRECTORY)

    def _install_config_yaml(self: PWN) -> None:
        template: Template = ENVIRONMENT.get_template('circle-ci/stage-one/config.yaml')
        render_path: str = os.path.join(self._ci_directory_path, 'config.yaml')
        template_context: typing.Dict[str, typing.Any] = {}

        logger.info(f'Writing Stage One CircleCI Configuration to path[{render_path}]')
        with open(render_path, 'w') as stream:
            stream.write(template.render(**template_context))

        self._altered_files.append(render_path)

    def _install_build_branch_script(self: PWN) -> None:
        template: Template = ENVIRONMENT.get_template('circle-ci/stage-one/sync-build-branch.sh')
        render_path: str = os.path.join(self._ci_directory_path, 'sync-build-branch.sh')
        template_context: typing.Dict[str, typing.Any] = {}

        logger.info(f'Writing Stage One CircleCI script to path[{render_path}]')
        with open(render_path, 'w') as stream:
            stream.write(template.render(**template_context))

        self._altered_files.append(render_path)

    def install(self: PWN, overwrite: bool = False) -> None:
        if os.path.exists(self._ci_directory_path) and overwrite is True:
            shutil.rmtree(self._ci_directory_path)

        elif os.path.exists(self._ci_directory_path):
            raise ci_exceptions.InstallException(self._ci_directory_path)

        os.makedirs(self._ci_directory_path)

        self._install_config_yaml()
        self._install_build_branch_script()

    def uninstall(self: PWN) -> None:
        if os.path.exists(self._ci_directory_path):
            shutil.rmtree(self._ci_directory_path)
