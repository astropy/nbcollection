import pytest

from nbcollection_tests.ci.tools import executed_notebook_collection

ENCODING = 'utf-8'

def test_metadata():
    pass

def test__reset_notebook_execution(executed_notebook_collection):
    import json

    from nbcollection.ci.scanner.utils import find_build_jobs
    from nbcollection.ci.metadata.utils import reset_notebook_execution

    for job in find_build_jobs(executed_notebook_collection):
        for notebook in job.category.notebooks:
            with open(notebook.path, 'rb') as stream:
                notebook_data = json.loads(stream.read().decode(ENCODING))

            reset_notebook_execution(notebook_data)
            with open(notebook.path, 'wb') as stream:
                stream.write(json.dumps(notebook_data).encode(ENCODING))

            # Execute Notebook
