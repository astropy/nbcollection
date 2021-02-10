import enum
import typing


class CIEnvironment(enum.Enum):
    CircleCI = 'circle-ci'


class CIType(enum.Enum):
    CircleCI = 'circle-ci'
    GithubAcitons = 'github-actions'


class CICommandContext(typing.NamedTuple):
    project_path: str
    collection_names: typing.List[str]
    category_names: typing.List[str]
    notebook_names: typing.List[str]
