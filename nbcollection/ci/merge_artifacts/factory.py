import argparse

from nbcollection.ci.commands.utils import validate_and_parse_inputs
from nbcollection.ci.merge_artifacts.utils import artifact_merge

def run_merge_artifacts(options: argparse.Namespace) -> None:
    validate_and_parse_inputs(options)
    artifact_merge(options.project_path, options.repo_name, options.org,
            options.collection_names, options.category_names, options.notebook_names)
