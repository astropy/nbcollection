import logging
import typing

from nbcollection.ci.scanner.utils import load_gitignore_data
logger = logging.getLogger(__name__)

def build_categories(dir_path: str) -> types.GeneratorType:
    for root, dirnames, filenames in os.walk(dir_path):
        ignore = load_ignore_data(root)
        gitignore_filepath = os.path.join(dir_path, '.gitignore')
