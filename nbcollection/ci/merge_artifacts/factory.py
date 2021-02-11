import argparse

from nbcollection.ci.commands.utils import validate_and_parse_inputs
from nbcollection.ci.commands.datatypes import CICommandContext
from nbcollection.ci.merge_artifacts.utils import run_artifact_merge, generate_merge_context


def run_merge_artifacts(options: argparse.Namespace) -> None:
    validate_and_parse_inputs(options)
    command_context = CICommandContext(options.project_path,
                                     options.collection_names,
                                     options.category_names,
                                     options.notebook_names,
                                     options.ci_mode)

    merge_context = generate_merge_context(options.project_path, options.org, options.repo_name)
    run_artifact_merge(command_context, merge_context)
