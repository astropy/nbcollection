import hashlib
import os
import subprocess
import typing

ENCODING = 'utf-8'

def run_command(cmd: typing.Union[str, typing.List[str]], shell: bool=True) -> None:
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
