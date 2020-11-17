import logging
import os
import jinja2
import json
import requests
import shutil
import toml
import typing

from datetime import datetime

from jinja2.environment import Template, Environment

from nbcollection.ci.constants import ENCODING
from nbcollection.ci.datatypes import BuildJob
from nbcollection.ci.merge_artifacts.constants import CIRCLECI_TOKEN
from nbcollection.ci.scanner.utils import find_build_jobs

logger = logging.getLogger(__name__)

AUTHOR_DATE_FORMAT = '%Y-%m-%dT%H:%M:%S.000Z'
class CircleCIAuth(requests.auth.AuthBase):
    def __call__(self, request):
        request.headers['Circle-Token'] = CIRCLECI_TOKEN
        return request

class NotebookSource(typing.NamedTuple):
    filename: str
    filepath: str
    category: str
    collection: str
    url: str
    meta_file: bool

class ArtifactNotebook(typing.NamedTuple):
    title: str
    metadata: typing.Dict[str, typing.Any]
    filepath: str
    filename: str

class ArtifactCategory(typing.NamedTuple):
    name: str
    notebooks: typing.List[ArtifactNotebook]

class ArtifactCollection(typing.NamedTuple):
    name: str
    categories: typing.List[ArtifactCategory]

def artifact_merge(project_path: str, repo_name: str, org: str,
        collection_names: typing.List[str], category_names: typing.List[str], notebook_names: typing.List[str]) -> None:
    assert not CIRCLECI_TOKEN is None
    artifact_dest_dir = os.path.join(project_path, 'pages')
    if os.path.exists(artifact_dest_dir):
        shutil.rmtree(artifact_dest_dir)

    os.makedirs(artifact_dest_dir)
    module_dirpath = os.path.dirname(__file__)
    asserts_dir = os.path.join(module_dirpath, 'assets')
    template_dir = os.path.join(module_dirpath, 'template')
    environment_path = os.path.join(template_dir, 'environment.toml')
    site_dir = os.path.join(project_path, 'site')


    base_url = 'https://circleci.com/api/v1.1'
    recent_builds = f'{base_url}/recent-builds'
    project_url = f'{base_url}/project/github/{org}/{repo_name}'

    workspace_id = None
    ci_jobs = []
    artifact_urls = []
    project_builds = requests.get(project_url, auth=CircleCIAuth()).json()
    for idx, job in enumerate(project_builds):
        if idx == 0:
            last_author_date = datetime.strptime(job['author_date'], AUTHOR_DATE_FORMAT)
            ci_jobs.append(job)
            continue

        author_date = datetime.strptime(job['author_date'], AUTHOR_DATE_FORMAT)
        if last_author_date == author_date:
            ci_jobs.append(job)
            continue

        break

    for ci_job in ci_jobs:
        url = f'{base_url}/project/{ci_job["vcs_type"]}/{ci_job["username"]}/{ci_job["reponame"]}/{ci_job["build_num"]}/artifacts'
        resp = requests.get(url, auth=CircleCIAuth())
        artifact_urls.extend([a['url'] for a in resp.json() if not a['url'].endswith('index.html')])

    notebook_sources: typing.List[NotebookSource] = []
    for url in artifact_urls:
        filename = os.path.basename(url)
        filepath = os.path.join(artifact_dest_dir, filename)
        file_category = os.path.dirname(url).rsplit('/', 1)[-1]
        file_collection = os.path.dirname(url).rsplit('/', 2)[-2]
        meta_file = filename.endswith('metadata.json')
        resp = requests.get(url, auth=CircleCIAuth(), stream=True)
        logger.info(f'Storing File[{filepath}]')
        with open(filepath, 'wb') as stream:
            for content in resp.iter_content(chunk_size=1024):
                stream.write(content)

        notebook_sources.append(NotebookSource(filename, filepath, file_category, file_collection, url, meta_file))

    existing_categories = [item for item in set(['.'.join([nb.collection, nb.category]) for nb in notebook_sources])]
    for job in find_build_jobs(project_path, collection_names, category_names, notebook_names):
        namespace = '.'.join([job.collection.name, job.category.name])
        if namespace in existing_categories:
            continue

        for notebook in job.category.notebooks:
            html_filepath = f'{artifact_dest_dir}/{job.collection.name}/{job.category.name}/{notebook.name}.html'
            meta_filepath = f'{artifact_dest_dir}/{job.collection.name}/{job.category.name}/{notebook.name}.metadata.json'

            html_filename = os.path.basename(html_filepath)
            notebook_sources.append(NotebookSource(html_filename, html_filepath, job.category.name, job.collection.name, 'local-file', meta_filepath))

            meta_filename = os.path.basename(meta_filepath)
            notebook_sources.append(NotebookSource(meta_filename, meta_filepath, job.category.name, job.collection.name, 'local-file', meta_filepath))

    collections = {}
    for notebook in notebook_sources:
        coll = collections.get(notebook.collection, [])
        collections[notebook.collection] = coll
        coll.append(notebook)

    collection_categories = {}
    for coll_name, coll_source in collections.items():
        coll = collection_categories.get(coll_name, {})
        for notebook in coll_source:
            cat = coll.get(notebook.category, [])
            coll[notebook.category] = cat
            cat.append(notebook)

        collection_categories[coll_name] = coll

    NAME_ISSUES = [
        ('%20', ' '),
    ]
    artifact_collections = []
    for coll_name, coll_source in collection_categories.items():
        cats = []
        for cat_name, cat_source in coll_source.items():
            nbs = []
            for idx, notebook in enumerate(cat_source[::2]):
                cat_source_idx = idx * 2 + 1
                with open(cat_source[cat_source_idx].filepath, 'rb') as stream:
                    metadata = json.loads(stream.read().decode(ENCODING))

                for find, replace in NAME_ISSUES:
                    metadata['title'].replace(find, replace)

                nbs.append(ArtifactNotebook(metadata['title'], metadata, notebook.filepath, notebook.filename))

            for find, replace in NAME_ISSUES:
                cat_name = cat_name.replace(find, replace)

            cats.append(ArtifactCategory(cat_name, sorted(nbs)))

        for find, replace in NAME_ISSUES:
            coll_name = coll_name.replace(find, replace)

        artifact_collections.append(ArtifactCollection(coll_name, sorted(cats)))

    if os.path.exists(site_dir):
        shutil.rmtree(site_dir)

    os.makedirs(site_dir)
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

    def load_environment() -> typing.Dict[str, typing.Any]:
        environment = {}
        with open(environment_path, 'r') as stream:
            environment = toml.loads(stream.read())

        environment['today'] = datetime.utcnow()
        return environment

    jinja2_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), undefined=jinja2.StrictUndefined)
    _add_jinja2_filters(jinja2_environment)
    index: Template = jinja2_environment.get_template('index.html')
    environment = load_environment()
    template_context = {
        'page': {
            'title': environment['index_title'],
            'keywords': environment['keywords'],
            'description': environment['description'],
            'locale': environment['default_locale'],
            'author': environment['author'],
            'maintainer': environment['maintainer'],
            'url': f'{environment["website_base_url"]}/index.html',
        },
        'static_url': 'static/',
        'collections': artifact_collections,
    }
    index_filepath = os.path.join(site_dir, 'index.html')
    with open(index_filepath, 'wb') as stream:
        stream.write(index.render(**template_context).encode(ENCODING))

    for coll in artifact_collections:
        for cat in coll.categories:
            for notebook in cat.notebooks:
                dest_filepath = os.path.join(site_dir, coll.name, cat.name, notebook.filename)
                for find, replace in NAME_ISSUES:
                    dest_filepath = dest_filepath.replace(find, replace)

                dest_dirpath = os.path.dirname(dest_filepath)
                if not os.path.exists(dest_dirpath):
                    os.makedirs(dest_dirpath)

                shutil.copyfile(notebook.filepath, dest_filepath)
