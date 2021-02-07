import logging
import tempfile
import typing

from nbcollection_tests.ci.tools.integrations import \
        github as github_integration, \
        local as local_integration
from nbcollection_tests.ci.tools.integrations.datatypes import RepoType, Template


PWN: typing.TypeVar = typing.TypeVar('PWN')
logger = logging.getLogger(__name__)


class TestRepo:
    repo_type: RepoType
    repo_path: str

    def __init__(self: PWN, repo_type: RepoType, template: Template, repo_path: str = None) -> None:
        self.repo_type = repo_type
        self.template = template
        self.repo_path = repo_path or tempfile.NamedTemporaryFile().name

    def __enter__(self: PWN) -> None:
        return self.setup()

    def __exit__(self: PWN, *args, **kwargs) -> None:
        self.destroy()

    @property
    def repo_name(self: PWN) -> str:
        return self.repo_path.rsplit('/', 1)[1]

    def setup(self: PWN) -> typing.Union[
            github_integration.GithubRepo,
            local_integration.LocalRepo]:
        if self.repo_type is RepoType.Github:
            github_repo = github_integration.Integrate().Repo(self.repo_name).create()
            github_repo.fill(self.template)
            # self._repo.create_remote('origin', url=github_repo.git_url)
            # logger.info(f'Pushing repo data to Github[{github_repo.https_url}]')
            # self._repo.remotes[0].push('master')
            return github_repo

        elif self.repo_type is RepoType.Local:
            local_repo = local_integration.Integrate().Repo(self.repo_path).create()
            local_repo.fill(self.template)
            return local_repo

        raise NotImplementedError(self.repo_type)

    def destroy(self: PWN) -> None:
        if self.repo_type is RepoType.Github:
            github_integration.Integrate().Repo(self.repo_name).destroy()

        elif self.repo_type is RepoType.Local:
            local_integration.Integrate().Repo(self.repo_path).destroy()

        else:
            raise NotImplementedError(self.repo_type)

        self.repo_type = None
