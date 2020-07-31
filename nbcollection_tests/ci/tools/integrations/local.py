import git
import os
import logging
import shutil
import typing

from nbcollection_tests.ci.tools.integrations import constants

PWN: typing.TypeVar = typing.TypeVar('PWN')
logger = logging.getLogger(__name__)

class LocalRepo:
    """
    This integration makes sure that all repos created don't already exists. If the exist, the logic is meant to fail.
      Currently, handling how the logic fails is not implemented
    """
    _repo: git.repo.base.Repo
    repo_path: str

    def __init__(self: PWN, repo_path: str) -> None:
        self.repo_path = repo_path

    def create(self: PWN) -> PWN:
        if os.path.exists(self.repo_path):
            raise NotImplementedError

        return self

    def destroy(self: PWN) -> None:
        if os.path.exists(self.repo_path):
            shutil.rmtree(self.repo_path)

    def fill(self: PWN) -> None:
        """
        Fills the repo with fake repo-data
        """
        if not os.path.exists(self.repo_path):
            logger.info(f'Copying Notebook CI Template Repo to RepoPath[{self.repo_path}]')
            shutil.copytree(constants.CI_REPO_TEMPLATE_PATH, self.repo_path)
            self._repo = git.Repo.init(self.repo_path)
            for filepath in self._repo.untracked_files:
                self._repo.index.add(filepath)

            self._repo.index.commit('Generated Repository for https://github.com/adrn/nbcollection Integration Testing')
        else:
            raise NotImplementedError

class Integrate:
    """
    Integrate takes on the model of a Factory pattern. It returns Repo-Type objects. Validation only needs to happen
        once during the lifecycle of the program. Handling service outages is currently out of scope
    """
    __state: typing.Dict[str, str] = {}
    def Repo(self: PWN, repo_path: str) -> str:
        if self.__state.get('validated', False) is False:
            self.validate()
            self.__state['validated'] = True

        return LocalRepo(repo_path)

    def validate(self: PWN) -> None:
        pass

