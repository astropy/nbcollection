import pytest
import subprocess
import time
import typing

def run_command(cmd: typing.Union[str, typing.List[str]]) -> None:
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    while proc.poll() is None:
        time.sleep(.1)

    if proc.poll() > 0:
        raise NotImplementedError(f'Exit Code: {proc.poll()}')

def test__all_command_help():
    from nbcollection.ci import __main__ as main_module

    for name, command in main_module.commands.items():
        python_bin = '/home/jbcurtin/.pyenv/shims/python'
        cmd = f"""PYTHONPATH='.' python -m nbcollection.ci {name} -h"""
        run_command(cmd)
