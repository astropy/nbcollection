import pytest

from nbcollection.ci.constants import ENCODING
from nbcollection_tests.ci.tools import executed_notebook_collection, metadata_rich_notebooks

def test__reset_notebook_execution(executed_notebook_collection):
    import json
    import os

    from nbcollection.ci.scanner.utils import find_build_jobs
    from nbcollection.ci.metadata.utils import reset_notebook_execution
    from nbcollection_tests.ci.tools.utils import collection_set_to_namespace

    notebook_paths = []
    for job in find_build_jobs(executed_notebook_collection):
        for notebook in job.category.notebooks:
            with open(notebook.path, 'rb') as stream:
                notebook_data = json.loads(stream.read().decode(ENCODING))

            reset_notebook_execution(notebook_data)
            with open(notebook.path, 'wb') as stream:
                stream.write(json.dumps(notebook_data).encode(ENCODING))

            notebook_paths.append(notebook.path)

    for path in notebook_paths:
        assert os.path.exists(path)
        with open(path, 'rb') as stream:
            notebook_data = json.loads(stream.read().decode(ENCODING))

        for cell in notebook_data['cells']:
            assert cell.get('execution_count', None) is None
            assert len(cell.get('outputs', [])) == 0

    # Execute Notebooks

def test__reset_notebook_execution__interface(executed_notebook_collection):
    import json
    import os

    from nbcollection.ci.constants import SCANNER_BUILD_DIR
    from nbcollection.ci.scanner.utils import find_build_jobs, generate_job_context
    from nbcollection.ci.metadata.factory import run_reset_notebook_execution
    from nbcollection.ci.commands.utils import validate_and_parse_inputs
    from nbcollection.ci.metadata.utils import reset_notebook_execution
    from nbcollection_tests.ci.tools.utils import collection_set_to_namespace

    options = collection_set_to_namespace(executed_notebook_collection)
    run_reset_notebook_execution(options)
    for job in find_build_jobs(options.project_path, options.collection_names, options.category_names, options.notebook_names):
        job_context = generate_job_context(job)
        for notebook in job.category.notebooks:
            notebook_path = os.path.join(SCANNER_BUILD_DIR, job.semantic_path(), f'{notebook.name}.ipynb')
            assert os.path.exists(notebook_path)
            with open(notebook_path, 'rb') as stream:
                notebook_data = json.loads(stream.read().decode(ENCODING))

            for idx, cell in enumerate(notebook_data['cells']):
                assert cell.get('execution_count', None) is None
                assert len(cell.get('outputs', [])) == 0


def test__extract_metadata(metadata_rich_notebooks):
    import json
    import os

    from nbcollection.ci.constants import SCANNER_BUILD_DIR
    from nbcollection.ci.datatypes import Metadata
    from nbcollection.ci.scanner.utils import find_build_jobs, generate_job_context
    from nbcollection.ci.metadata.utils import extract_metadata

    metadata_keys = ['title', 'description']
    for job in find_build_jobs(metadata_rich_notebooks):
        job_context = generate_job_context(job)
        for notebook_context in job_context.notebooks:
            extract_metadata(notebook_context)
            assert os.path.exists(notebook_context.metadata.path)
            with open(notebook_context.metadata.path, 'rb') as stream:
                extracted_data = json.loads(stream.read().decode(ENCODING))
                assert extracted_data['title'] == 'Notebook One'
                assert not extracted_data['description'] is None

def test__extract_metadata__interface(metadata_rich_notebooks):
    import json
    import os

    from nbcollection.ci.constants import SCANNER_BUILD_DIR
    from nbcollection.ci.datatypes import Metadata
    from nbcollection.ci.scanner.utils import find_build_jobs, generate_job_context
    from nbcollection.ci.metadata.factory import run_extract_metadata
    from nbcollection.ci.metadata.utils import extract_metadata
    from nbcollection.ci.commands.utils import validate_and_parse_inputs
    from nbcollection_tests.ci.tools.utils import collection_set_to_namespace

    metadata_keys = ['title', 'description']
    notebook_name = 'Notebook-One'
    options = collection_set_to_namespace(metadata_rich_notebooks, extra={
        'notebook_names': notebook_name,
    })
    run_extract_metadata(options)
    for job_idx, job in enumerate(find_build_jobs(options.project_path, options.collection_names, options.category_names, options.notebook_names)):
        for notebook in job.category.notebooks:
            extract_metadata(notebook)
            with open(notebook.metadata.path, 'rb') as stream:
                metadata = json.loads(stream.read().decode(ENCODING))
                for key in metadata_keys:
                    assert key in metadata.keys()

    assert job_idx == 0
    validative_options = collection_set_to_namespace(metadata_rich_notebooks, extra={
        'notebook_names': notebook_name,
    })
    validate_and_parse_inputs(validative_options)
    for job_idx, job in enumerate(find_build_jobs(options.project_path, options.collection_names, options.category_names, options.notebook_names)):
        job_context = generate_job_context(job)
        for notebook_idx, notebook_context in enumerate(job_context.notebooks):
            extract_metadata(notebook_context)

        assert notebook_idx == 0

        validative_metadata_filepath = os.path.join(SCANNER_BUILD_DIR, job.semantic_path(), f'{notebook.name}.metadata.json')
        with open(validative_metadata_filepath, 'rb') as stream:
            validative_metadata = json.loads(stream.read().decode(ENCODING))
            for key in metadata_keys:
                assert validative_metadata[key] == metadata[key]

    assert job_idx == 0
