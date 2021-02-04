import argparse
import jinja2
import logging
import os
import typing

from jinja2.environment import Environment

from nbcollection.ci.generator.circle_ci import CircleCiRepo

TEMPLATES_DIR: str = os.path.join(os.path.dirname(__file__), 'templates')
ENVIRONMENT: Environment = jinja2.Environment(  # nosec
        loader=jinja2.FileSystemLoader(TEMPLATES_DIR),  # nosec
        autoescape=jinja2.select_autoescape(['html', 'xml']))  # nosec
logger = logging.getLogger(__name__)


def render_circle_ci(args: argparse.Namespace) -> typing.Any:
    with CircleCiRepo(args.repo_path) as ci:
        if args.uninstall:
            logger.info('Uninstalling CircleCI')
            ci.uninstall()
            logger.info('CircleCI Uninstalled')

        else:
            logger.info('Installing CircleCI')
            ci.install(args.overwrite)
            logger.info('CircleCI Installed')
