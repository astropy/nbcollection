
"""
This module contains functionality to check notebooks for possible problems like
executed cells that were erroneously checked in.
"""

import os
import sys
import nbformat
import logging

log = logging.getLogger('check_nbs')


def is_executed(nb_path):
    nb = nbformat.read(nb_path, nbformat.NO_CONVERT)
    for cell in nb.cells:
        if cell.cell_type == 'code':
            if cell.outputs:
                return True
    return False


def execution_check(name, full_path):
    log.info('Checking notebook {}'.format(name))
    success = True
    if is_executed(full_path):
        log.error('Notebook {} has executed cells!'.format(name))
        success = False

    return success


def visit_content_nbs(nbpath, visitfunc):
    """
    Visits all the notebooks in the ``nbpath`` that are *not* "exec_*" or in
    ipynb_checkpoints, and calls the ``visitfunc`` on them. Signature of
    ``visitfunc`` should be ``visitfunc(name, nb_full_path)``.
    """
    success = True
    for root, dirs, files in os.walk(nbpath):
        for name in files:
            _, ext = os.path.splitext(name)
            full_path = os.path.join(root, name)
            if ext != '.ipynb':
                continue

            if name.startswith('exec_'):  # skip the executed ones
                continue

            if 'ipynb_checkpoints' in full_path:  # skip checkpoint saves
                continue

            success = visitfunc(name, full_path) and success
    return success


def main():
    """
    Call this to programmatically use this as a command-line script
    """
    logging.basicConfig()
    log.setLevel(logging.INFO)
    success = visit_content_nbs('.', execution_check)
    if success:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == '__main__':
    main()
