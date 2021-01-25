import enum


class CIEnvironment(enum.Enum):
    CircleCI = 'circle-ci'


class CIType(enum.Enum):
    CircleCI = 'circle-ci'
    GithubAcitons = 'github-actions'


class VirtualENVType(enum.Enum):
    # https://docs.python.org/3/library/venv.html
    VENV = 'python-venv'
    # https://virtualenv.pypa.io/en/latest/user_guide.html
    VirtualENV = 'virtualenv'
    # https://docs.conda.io/projects/conda/en/latest/api/index.html
    Conda = 'conda'
    # https://docs.conda.io/en/latest/miniconda.html
    MiniConda = 'mini-conda'
    # https://github.com/jhunkeler/spmc
    SPM = 'smpc'
