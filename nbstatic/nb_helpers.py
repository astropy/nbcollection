import re
import nbformat

__all__ = ['is_executed', 'get_title']


def is_executed(nb_path):
    nb = nbformat.read(nb_path, nbformat.NO_CONVERT)
    for cell in nb.cells:
        if cell.cell_type == 'code':
            if cell.outputs:
                return True
    return False


def get_title(nb_path):
    # read the first top-level header as the notebook title
    with open(nb_path) as f:
        nb = nbformat.read(f, as_version=4)  # TODO: make config item?

    for cell in nb['cells']:
        match = re.search('# (.*)', cell['source'])

        if match:
            break

    else:
        raise RuntimeError("Failed to find a title for the notebook. To include"
                           " it in an index page, each notebook must have a H1 "
                           "heading that is treated as the notebooks title.")

    title = match.groups()[0]

    return title
