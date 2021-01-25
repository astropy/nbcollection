import contextlib
import os
import typing
import types


@contextlib.contextmanager
def ActivateENVVars(env_vars: typing.Dict[str, str]) -> types.GeneratorType:
    for key, value in env_vars.items():
        if not isinstance(key, str):
            raise NotImplementedError

        elif not isinstance(value, (str, int)):
            raise NotImplementedError

        os.environ[key] = str(value)

    yield None

    for key, value in env_vars.items():
        del os.environ[key]
