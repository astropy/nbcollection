import argparse

from nbcollection.ci.commands.utils import validate_and_parse_inputs
from nbcollection.ci.scanner.utils import find_build_jobs
from nbcollection.ci.generate_ci_environment.utils import gen_ci_env

def run_generate_ci_environment(options: argparse.Namespace) -> None:
    validate_and_parse_inputs(options)
    jobs = []
    for job in find_build_jobs(
            options.project_path,
            options.collection_names,
            options.category_names,
            options.notebook_names):
        jobs.append(job)

    gen_ci_env(jobs, options.ci_environment, options.project_path)
