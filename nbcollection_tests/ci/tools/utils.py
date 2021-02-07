import argparse
import hashlib
import os
import subprocess
import time
import tempfile
import typing

from nbcollection.ci.scanner.utils import find_build_jobs

ENCODING = 'utf-8'


def run_command(cmd: typing.Union[str, typing.List[str]], shell: bool = True) -> None:
    if isinstance(cmd, str):
        cmd = [cmd]

    proc = subprocess.Popen(cmd, shell=shell)
    while proc.poll() is None:
        time.sleep(.1)


def map_filesystem(directory_path: str) -> typing.List[str]:
    files: typing.List[str] = []
    for root, directories, filenames in os.walk(directory_path):
        for dirname in directories:
            dirpath: str = os.path.join(root, dirname)
            files.extend(map_filesystem(dirpath))

        for filename in filenames:
            filepath: str = os.path.join(root, filename)
            files.append(filepath)

    # Consistent to Python rather than how the os.walk implementation
    return sorted(files)


def hash_filesystem(directory_path: str) -> str:
    fs_map = map_filesystem(directory_path)
    return hashlib.sha256(''.join(fs_map).encode(ENCODING)).hexdigest()


def collection_set_to_namespace(path_to_collection_set, extra: typing.Dict[str, typing.Any] = {}):
    collection_names = []
    category_names = []
    for job in find_build_jobs(path_to_collection_set):
        if job.collection.name not in collection_names:
            collection_names.append(job.collection.name)

        if job.category.name not in category_names:
            category_names.append(job.category.name)

    kwargs = {
        'project_path': path_to_collection_set,
        'collection_names': ','.join(collection_names),
        'category_names': ','.join(category_names),
        'notebook_names': '',
        'output_dir': tempfile.NamedTemporaryFile().name
    }
    kwargs.update(extra)
    return argparse.Namespace(**kwargs)
