import argparse

from nbcollection.ci.commands.utils import validate_and_parse_inputs
from nbcollection.ci.scanner.utils import find_build_jobs, generate_job_context, run_job_context

def run_build(options: argparse.ArgumentParser) -> None:
    validate_and_parse_inputs(options)
    for job_idx, job in enumerate(find_build_jobs(
                                    options.project_path,
                                    options.collection_names,
                                    options.category_names,
                                    options.notebook_names)):
        job_context = generate_job_context(job)
        run_job_context(job_context, True)
