import requests
import typing

from nbcollection.ci.merge_artifacts.constants import CIRCLECI_TOKEN


class MergeContext(typing.NamedTuple):
    artifact_dest_dir: str
    module_dirpath: str
    # asserts_dir = os.path.join(module_dirpath, 'assets')
    template_dir: str
    environment_path: str
    site_dir: str
    project_url: str
    assets_dir: str


class CircleCIAuth(requests.auth.AuthBase):
    def __call__(self, request):
        if CIRCLECI_TOKEN is None:
            raise NotImplementedError('Missing ENVVar: CIRCLECI_TOKEN')

        request.headers['Circle-Token'] = CIRCLECI_TOKEN
        return request


class NotebookSource(typing.NamedTuple):
    filename: str
    filepath: str
    category: str
    collection: str
    url: str
    meta_file: bool


class ArtifactNotebook(typing.NamedTuple):
    title: str
    metadata: typing.Dict[str, typing.Any]
    filepath: str
    filename: str


class ArtifactCategory(typing.NamedTuple):
    name: str
    notebooks: typing.List[ArtifactNotebook]


class ArtifactCollection(typing.NamedTuple):
    name: str
    categories: typing.List[ArtifactCategory]
