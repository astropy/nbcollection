import logging
import git
import json
import os
import tempfile
import requests
import shutil
import typing

from nbcollection_tests.ci import exceptions as ci_test_exceptions
from nbcollection_tests.ci.tools import constants
from nbcollection_tests.ci.tools.integrations.datatypes import Template
from nbcollection_tests.ci.tools.integrations.utils import generate_template

from requests.auth import HTTPBasicAuth

PWN: typing.TypeVar = typing.TypeVar('PWN')
logger = logging.getLogger(__name__)

class GithubRepo:
    name: str
    _username: str
    _password: str
    def __init__(self: PWN, name: str) -> None:
        self.name = name
        self._username = os.environ['GITHUB_USERNAME']
        self._password = os.environ['GITHUB_TOKEN']
        self.repo_path = tempfile.NamedTemporaryFile().name

    @property
    def repo(self: PWN) -> str:
        if getattr(self, '_repo', None) is None:
            try:
                self._repo = git.Repo(self.repo_path)
            except git.exc.InvalidGitRepositoryError:
                logger.info(f'Cloning Repo Locally')
                self._repo = git.Repo.clone_from(self.https_url_with_auth, self._repo_path)

        return self._repo

    @property
    def https_url(self: PWN) -> str:
        return f'https://github.com/{self._username}/{self.name}.git'

    @property
    def https_url_with_auth(self: PWN) -> str:
        return f'https://{self._username}:{self._password}@github.com/{self._username}/{self.name}.git'

    @property
    def git_url(self: PWN) -> str:
        return f'git@github.com:{self._username}/{self.name}.git'

    def create(self: PWN) -> PWN:
        url: str = 'https://api.github.com/user/repos'
        logger.info(f'Creating Repo[{self.https_url}]')
        try:
            response: requests.models.Response = requests.post(url, data=json.dumps({
                'name': self.name,
            }), headers={
                'Accept': 'application/vnd.github.baptiste-preview+json',
            }, auth=HTTPBasicAuth(self._username, self._password))
        except Exception as err:
            # import pdb; pdb.set_trace()
            raise err

        else:
            if response.status_code != 201:
                raise ci_test_exceptions.GithubInvalidAuthorization("Unable to create repo. Please regenerate token with correct perms: https://github.com/settings/tokens/")

        return self

    def destroy(self: PWN) -> PWN:
        url: str = f'https://api.github.com/repos/{self._username}/{self.name}'
        logger.info(f'Destroying Repo[{self.https_url}]')
        if os.path.exists(self.repo_path):
            shutil.rmtree(self.repo_path)

        try:
            response: requests.models.Response = requests.delete(url,
                    auth=HTTPBasicAuth(self._username, self._password))
        except Exception as err:
            # import pdb; pdb.set_trace()
            raise err

        else:
            if response.status_code != 204:
                raise ci_test_exceptions.GithubInvalidAuthorization(f"'delete_repo' auth required. https://developer.github.com/v3/repos/#delete-a-repository. Please regenerate token with correct perms: https://github.com/settings/tokens/")

    def fill(self: PWN, template: Template) -> None:
        """
        Fills the repo with fake-repo-data
        """
        logging.info(f'Copying Notebook CI Template Repo to RepoPath[{self.repo_path}]')
        generate_template(Template.Initial, self.repo_path)
        # shutil.copytree(constants.CI_REPO_TEMPLATE_PATH, self.repo_path)
        git.Repo.init(self.repo_path)
        for filepath in self.repo.untracked_files:
            self.repo.index.add(filepath)

        self.repo.index.commit('Generated Repository for https://github.com/adrn/nbcollection Integration Testing')
        remote_name: str = 'origin'
        branch_name: str = 'main'
        logger.info(f'Pushing Local Repo to Github Repo: Remote[{remote_name}], Branch[{branch_name}]')
        self.repo.create_remote(remote_name, url=self.https_url_with_auth)
        new_head = self.repo.create_head(branch_name)
        new_head.checkout()
        self.repo.remotes[0].push(branch_name)

class Integrate:
    __state: typing.Dict[str, str] = {}
    def Repo(self: PWN, name: str) -> str:
        if self.__state.get('validated', False) is False:
            self.validate()
            self.__state['validated'] = True

        return GithubRepo(name)

    def _test_connection(self: PWN) -> None:
        if os.environ.get('GITHUB_USERNAME', None) is None:
            raise ci_test_exceptions.MissingENVVarException('GITHUB_USERNAME')

        if os.environ.get('GITHUB_TOKEN', None) is None:
            raise ci_test_exceptions.MissingENVVarException('GITHUB_TOKEN')


    def _test_permissions(self: PWN) -> None:
        repo_name: str = tempfile.NamedTemporaryFile().name.rsplit('/', 1)[1]
        repo = GithubRepo(repo_name)
        repo.create()
        repo.destroy()

    def validate(self: PWN) -> None:
        self._test_connection()
        self._test_permissions()

