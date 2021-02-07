import enum


class CIEnvironment(enum.Enum):
    CircleCI = 'circle-ci'


class CIType(enum.Enum):
    CircleCI = 'circle-ci'
    GithubAcitons = 'github-actions'
