import argparse
import json

from nbcollection.ci.commands.utils import validate_and_parse_inputs
from nbcollection.ci.constants import ENCODING
from nbcollection.ci.datatypes import Metadata
from nbcollection.ci.scanner.utils import find_build_jobs, generate_job_context
from nbcollection.ci.metadata.utils import reset_notebook_execution, extract_metadata

def run_reset_notebook_execution(options: argparse.Namespace) -> None:
    validate_and_parse_inputs(options)
    for job in find_build_jobs(options.project_path, options.collection_names, options.category_names):
        for notebook in job.category.notebooks:
            with open(notebook.path, 'rb') as stream:
                notebook_data = json.loads(stream.read().decode(ENCODING))

            reset_notebook_execution(notebook_data)

            with open(notebook.path, 'wb') as stream:
                stream.write(json.dumps(notebook_data).encode(ENCODING))

def run_extract_metadata(options: argparse.Namespace) -> Metadata:
    validate_and_parse_inputs(options)
    for job in find_build_jobs(options.project_path, options.collection_names, options.category_names, options.notebook_names):
        job_context = generate_job_context(job)
        for notebook_context in job_context.notebooks:
            extract_metadata(notebook_context)
