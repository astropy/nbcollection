#!/usr/bin/env python

import bs4
import logging
import jinja2
import os
import shutil
import toml
import typing

from datetime import datetime

from jinja2.environment import Template, Environment

from nbcollection.ci.constants import ENCODING
from nbcollection.ci.merge_artifacts.datatypes import MergeContext, ArtifactCollection

logger = logging.getLogger(__file__)


def add_jinja2_filters(environment: Environment) -> None:
    def _render_human_datetime(datetime: datetime) -> str:
        return datetime.strftime('%A, %d. %B %Y %I:%M%p')

    def _render_machine_datetime(datetime: datetime) -> str:
        return datetime.strftime('%Y-%m-%d')

    def _render_machine_datetime_with_time(datetime: datetime) -> str:
        return datetime.strftime('%Y-%m-%dT%H-%M-%S')

    environment.filters['human_date'] = _render_human_datetime
    environment.filters['machine_date'] = _render_machine_datetime
    environment.filters['machine_date_with_time'] = _render_machine_datetime_with_time


def load_environment(merge_context: MergeContext) -> typing.Dict[str, typing.Any]:
    environment = {}
    with open(merge_context.environment_path, 'r') as stream:
        environment = toml.loads(stream.read())

    environment['today'] = datetime.utcnow()
    environment['keywords'] = ','.join(environment['keywords'])
    return environment


def load_template(template_name: str, merge_context: MergeContext) -> Template:
    JINJA2_ENVIRONMENT = None
    if JINJA2_ENVIRONMENT is None:
        JINJA2_ENVIRONMENT = jinja2.Environment(loader=jinja2.FileSystemLoader(merge_context.template_dir),  # nosec
                                                undefined=jinja2.StrictUndefined)  # nosec
        add_jinja2_filters(JINJA2_ENVIRONMENT)

    return JINJA2_ENVIRONMENT.get_template(template_name)


def render_notebook_template(notebook_filepath: str, merge_context: MergeContext) -> None:
    with open(notebook_filepath, 'rb') as stream:
        notebook_content = stream.read().decode(ENCODING)

    notebook_template = load_template('notebook.html', merge_context)
    environment = load_environment(merge_context)
    notebook_filename = os.path.basename(notebook_filepath)
    template_context = {
        'page': {
            'title': environment['notebook_title'],
            'keywords': environment['notebook_keywords'],
            'description': environment['notebook_description'],
            'locale': environment['locale'],
            'author': environment['author'],
            'maintainer': environment['maintainer'],
            'url': '{environment["website_base_url"]}/notebooks/{notebook_filename}',
        },
        'static_url': 'static/',
        'notebook_content': notebook_content,
    }
    with open(notebook_filepath, 'wb') as stream:
        stream.write(notebook_template.render(**template_context).encode(ENCODING))


def render_index(merge_context: MergeContext, artifact_collections: typing.List[ArtifactCollection]) -> None:
    index = load_template('index.html', merge_context)
    environment = load_environment(merge_context)
    template_context = {
        'page': {
            'title': environment['index_title'],
            'keywords': environment['keywords'],
            'description': environment['description'],
            'locale': environment['locale'],
            'author': environment['author'],
            'maintainer': environment['maintainer'],
            'url': f'{environment["website_base_url"]}/index.html',
        },
        'static_url': 'static/',
        'collections': artifact_collections,
    }
    index_filepath = os.path.join(merge_context.site_dir, 'index.html')
    with open(index_filepath, 'wb') as stream:
        stream.write(index.render(**template_context).encode(ENCODING))


def extract_cells_from_html(filepath: str) -> None:
    with open(filepath, 'rb') as stream:
        soup = bs4.BeautifulSoup(stream.read().decode(ENCODING), 'lxml')

    cell_data = []
    for cell in soup.findAll('div', {'class': 'cell'}):
        cell_data.append(str(cell))

    cell_data = '\n'.join(cell_data)
    with open(filepath, 'wb') as stream:
        stream.write(cell_data.encode(ENCODING))


def render_static_assets(initial_dir: str, target_dir: str) -> None:
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    for root, dirnames, filenames in os.walk(initial_dir):
        for dirname in dirnames:
            render_static_assets(f'{initial_dir}/{dirname}', f'{target_dir}/{dirname}')

        for filename in filenames:
            target_filepath = os.path.join(target_dir, filename)
            source_filepath = os.path.join(initial_dir, filename)
            if any([
                filename.endswith('.css'),
                filename.endswith('.png'),
                filename.endswith('.jpg'),
                filename.endswith('.jpeg'),
                filename.endswith('.svg'),
                filename.endswith('.gif')]):
                logger.info(f'Moving File[{filename}] from Asset Dir -> Target Dir')
                shutil.copyfile(source_filepath, target_filepath)
            else:
                raise NotImplementedError(filename)

        break
