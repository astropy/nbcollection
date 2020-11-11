import json
import os
import typing

from nbcollection.ci.constants import ENCODING
from nbcollection.ci.exceptions import MetadataExtractionError
from nbcollection.ci.datatypes import NotebookContext, MetadataContext
from nbcollection.ci.commands.utils import validate_and_parse_inputs

def reset_notebook_execution(notebook_data: typing.Dict[str, typing.Any]) -> None:
    for cell in notebook_data['cells']:
        if cell['cell_type'] == 'code':
            cell['outputs'] = []
            cell['execution_count'] = None

def extract_metadata(notebook: NotebookContext) -> None:
    details = {key: None for key in ['title', 'description']}
    with open(notebook.path, 'rb') as stream:
        notebook_data = json.loads(stream.read().decode(ENCODING))
        for idx, cell in enumerate(notebook_data['cells']):
            if idx == 0:
                if not cell['cell_type'] in ['markdown']:
                    raise MetadataExtractionError(f'Unable to parse Title Cell from Notebook[{notebook.name}]')

                cell_rest = []
                for line_idx, line_item in enumerate(cell['source']):
                    if line_item.strip().startswith('#') and details['title'] is None and line_idx == 0:
                        details['title'] = line_item.strip('# \n')
                        continue

                    cell_rest.append(line_item.strip(' \n'))

                details['description'] = '\n'.join(cell_rest)
                details['description'] = details['description'].strip('\n')
                continue

            if idx == 1 and cell['cell_type'] in ['markdown']:
                details['description'] = ' '.join(cell['source'])
                details['description'] = details['description'].strip('\n')

    dirpath = os.path.dirname(notebook.metadata.path)
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)

    with open(notebook.metadata.path, 'wb') as stream:
        stream.write(json.dumps(details, indent=2).encode(ENCODING))
