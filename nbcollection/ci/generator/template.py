import logging
import jinja2
import os

from jinja2.environment import Environment

logger = logging.getLogger(__name__)
TEMPLATES_DIR: str = os.path.join(os.path.dirname(__file__), 'template-files')
logger.info(f'CI Template Dir: {TEMPLATES_DIR}')
ENVIRONMENT: Environment = jinja2.Environment(  # nosec
        loader=jinja2.FileSystemLoader(TEMPLATES_DIR),  # nosec
        autoescape=jinja2.select_autoescape(['html', 'xml']))  # nosec
