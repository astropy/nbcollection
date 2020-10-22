import argparse
import typing

def reset_notebook_execution(notebook_data: typing.Dict[str, typing.Any]) -> None:
    for cell in notebook_data['cells']:
        if cell['cell_type'] == 'code':
            cell['outputs'] = []
            cell['execution_count'] = None
