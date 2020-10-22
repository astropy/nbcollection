from nbcollection.ci.scanner import find_build_jobs

def extract_metadata(options: argparse.Namespace) -> None:
    metadata = {}
    notebook_filename = os.path.basename(options.input)

