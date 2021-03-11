import enum
import typing


class BuildMode(enum.Enum):
    Concurrent = 'concurrent'
    Single = 'single'


class CIEnvironment(enum.Enum):
    CircleCI = 'circle-ci'


class CIType(enum.Enum):
    CircleCI = 'circle-ci'
    GithubAcitons = 'github-actions'


class CIMode(enum.Enum):
    Both = 'both'
    Online = 'online'
    Local = 'local'


class CICommandContext(typing.NamedTuple):
    project_path: str
    collection_names: typing.List[str]
    category_names: typing.List[str]
    notebook_names: typing.List[str]
    mode: CIMode


class Site(enum.Enum):
    GithubPages = 'github pages'
