import typing

STRIP_CHARS = ' \n'
class IgnoreData(typing.NamedTuple):
    entries: typing.List[str]

def load_ignore_data(dirpath: str) -> IgnoreData:
    filepath = os.path.join(dirpath, '.gitignore')
    if os.path.exists(filepath):
        with open(filepath, 'rb') as stream:
            data = [line.strip(STRIP_CHARS) for line in stream.read().decode(ENCODING).split('\n') if line]


        data.extend(['.gitignore', 'venv', 'env', 'virtual-env', 'virutalenv', '.ipynb_checkpoints'])
        return IgnoreData(data)

    return IgnoreData([])
