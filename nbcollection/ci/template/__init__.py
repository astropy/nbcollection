import logging
import jinja2
import os
import typing

from jinja2.environment import Environment, Template

logger = logging.getLogger(__name__)
TEMPLATES_DIR: str = os.path.join(os.path.dirname(__file__), 'template-files')
logger.info(f'CI Template Dir: {TEMPLATES_DIR}')
ENVIRONMENT: Environment = jinja2.Environment(loader=jinja2.FileSystemLoader(TEMPLATES_DIR),  # nosec
                                              autoescape=jinja2.select_autoescape(['html', 'xml']))  # nosec


def render(template_path: str, template_context: typing.Dict[str, typing.Any], render_path: str = None) -> None:
    template: Template = ENVIRONMENT.get_template(template_path)

    if render_path is None:
        return template.render(**template_context)

    logger.info(f'Rendering Template[{template_path}] to Path[{render_path}]')
    with open(render_path, 'w') as stream:
        stream.write(template.render(template_context))
