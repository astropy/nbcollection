"""Nbcollection configuration."""

from __future__ import annotations

from dataclasses import dataclass

__all__ = ["NbcollectionConfig"]


@dataclass
class NbcollectionConfig:
    """Nbcollection configuration.

    Attributes
    ----------
    github_repo_url : str or None
        URL of the GitHub repository hosting the notebooks.
    github_repo_path : str
        Root path of the notebooks inside the GitHub repository. Default is
        an empty string corresponding to the root of the repository.
    github_repo_branch : str
        Branch of the GitHub repository to use. Default is "main".
    """

    github_repo_url: str | None = None
    github_repo_path: str = ""
    github_repo_branch: str = "main"
