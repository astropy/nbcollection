import jinja2
import os
import toml
import typing

from datetime import datetime

from nbcollection.ci.exceptions import RendererException
from nbcollection.ci.constants import RENDERER_ENV_CONTEXT_PATH, RENDERER_TEMPLATE_DIR, ENCODING

from jinja2.environment import Environment, Template

def _add_jinja2_filters(environment: Environment) -> None:
    def _render_human_datetime(datetime: datetime) -> str:
        return datetime.strftime('%A, %d. %B %Y %I:%M%p')

    def _render_machine_datetime(datetime: datetime) -> str:
        return datetime.strftime('%Y-%m-%d')

    def _render_machine_datetime_with_time(datetime: datetime) -> str:
        return datetime.strftime('%Y-%m-%dT%H-%M-%S')

    environment.filters['human_date'] = _render_human_datetime
    environment.filters['machine_date'] = _render_machine_datetime
    environment.filters['machine_date_with_time'] = _render_machine_datetime_with_time

def load_env_context() -> typing.Dict[str, typing.Any]:
    environment: typing.Dict[str, typing.Any]
    if os.path.exists(RENDERER_ENV_CONTEXT_PATH):
        with open(RENDERER_ENV_CONTEXT_PATH, 'rb') as stream:
            environment = toml.loads(stream.read().decode(ENCODING))

    else:
        environment = {}

    environment['today'] = datetime.utcnow()
    return environment

def render_template(template_path: str, context: typing.Dict[str, typing.Any]) -> str:
    environment = jinja2.Environment(loader=jinja2.FileSystemLoader(RENDERER_TEMPLATE_DIR), undefined=jinja2.StrictUndefined)
    _add_jinja2_filters(environment)
    template = environment.get_template(template_path)
    context['environment'] = load_env_context()
    try:
        return template.render(**context)
    except jinja2.exceptions.UndefinedError as err:
        varname = err.args[0].rsplit("'", 2)[1]
        raise RendererException(f'Template Varible Missing[{varname}]')
