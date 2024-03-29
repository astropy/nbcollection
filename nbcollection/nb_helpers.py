"""Notebook utilities."""

import re

import nbformat

__all__ = ["is_executed", "get_title"]


def is_executed(nb_path):
    """Determine whether the notebook file has been executed.

    Parameters
    ----------
    nb_path : str
        The string path to a notebook file.

    Returns
    -------
    is_executed : bool
        True if the notebook has been executed.
    """
    nb = nbformat.read(nb_path, nbformat.NO_CONVERT)
    return any(cell.cell_type == "code" and cell.outputs for cell in nb.cells)


def get_title(nb_path):
    """Get the title of a notebook by finding the first H1 header.

    Parameters
    ----------
    nb_path : str
        The string path to a notebook file.

    Returns
    -------
    title : str
        The string title.
    """
    # read the first top-level header as the notebook title
    with open(nb_path) as f:
        nb = nbformat.read(f, as_version=4)  # TODO: make config item?

    for cell in nb["cells"]:
        match = re.search("# (.*)", cell["source"])

        if match:
            break

    else:
        msg = (
            "Failed to find a title for the notebook. To include it in an index page, "
            "each notebook must have a H1 heading that is treated as the notebooks "
            "title."
        )
        raise RuntimeError(msg)

    return match.groups()[0]
