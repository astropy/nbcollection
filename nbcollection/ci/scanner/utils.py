import os
import typing

from nbcollection.ci.constants import ENCODING

DEFAULT_IGNORE_ENTRIES = ['.gitignore', 'venv', 'env', 'virtual-env', 'virutalenv', '.ipynb_checkpoints']
STRIP_CHARS = ' \n'
class IgnoreData(typing.NamedTuple):
    entries: typing.List[str]

def load_ignore_data(dirpath: str) -> IgnoreData:
    entries = []
    for root, dirnames, filenames in os.walk(dirpath):
        for filename in filenames:
            if filename == '.gitignore':
                filepath = os.path.join(root, filename)
                with open(filepath, 'rb') as stream:
                    entries.extend([line.strip(STRIP_CHARS) for line in stream.read().decode(ENCODING).split('\n') if line])

    entries.extend(DEFAULT_IGNORE_ENTRIES)
    return IgnoreData(entries)
