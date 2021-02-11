import logging
import os
import jinja2
import json
import requests
import shutil
import sys
import toml
import types
import typing

from datetime import datetime

from nbcollection.ci.constants import ENCODING, AUTHOR_DATE_FORMAT
from nbcollection.ci.commands.datatypes import CICommandContext, CIMode
from nbcollection.ci.constants import CIRCLECI_TOKEN, SCANNER_ARTIFACT_DEST_DIR
from nbcollection.ci.merge_artifacts.datatypes import CircleCIAuth, NotebookSource, \
        ArtifactNotebook, ArtifactCategory, ArtifactCollection, MergeContext
from nbcollection.ci.merge_artifacts import html_builder
from nbcollection.ci.scanner.utils import find_build_jobs

logger = logging.getLogger(__name__)
JINJA2_ENVIRONMENT = None

# CircleCI
BASE_URL = 'https://circleci.com/api/v1.1'


def generate_merge_context(project_path: str, org: str, repo_name: str) -> MergeContext:
    artifact_dest_dir = os.path.join(project_path, 'pages')
    if os.path.exists(artifact_dest_dir):
        shutil.rmtree(artifact_dest_dir)

    # Filesystem modifications
    os.makedirs(artifact_dest_dir)

    module_dirpath = os.path.dirname(__file__)

    template_dir = os.environ.get('ARTIFACT_TEMPLATE_DIR', None)
    if template_dir is None:
        logger.info('Missing ENVVar ARTIFACT_TEMPLATE_DIR, using default Template')
        template_dir = os.path.join(module_dirpath, 'template')

    site_dir = os.path.join(project_path, 'site')
    if os.path.exists(site_dir):
        shutil.rmtree(site_dir)

    os.makedirs(site_dir)
    environment_path = os.path.join(template_dir, 'environment.toml')
    if not os.path.exists(environment_path):
        raise NotImplementedError(f'Missing Environment File: {environment_path}')

    assets_dir = os.path.join(template_dir, 'assets')
    if not os.path.exists(assets_dir):
        logger.warning(f'Assets Dir Missing: {assets_dir}')

    return MergeContext(
            artifact_dest_dir,
            module_dirpath,
            template_dir,
            environment_path,
            site_dir,
            f'{BASE_URL}/project/github/{org}/{repo_name}',
            assets_dir,
            SCANNER_ARTIFACT_DEST_DIR)


def latest_circleci_artifact_urls(merge_context: MergeContext) -> typing.List[str]:
    ci_jobs = []
    artifact_urls = []
    project_builds = requests.get(merge_context.project_url, auth=CircleCIAuth()).json()
    if len(project_builds) < 1:
        logger.info('No builds found. Aborting Artifact Merge')
        sys.exit(0)

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
        url = '/'.join([
            BASE_URL,
            'project',
            ci_job['vcs_type'],
            ci_job['username'],
            ci_job['reponame'],
            str(ci_job['build_num']),
            'artifacts'
        ])
        resp = requests.get(url, auth=CircleCIAuth())
        urls = [a['url'] for a in resp.json() if not a['url'].endswith('index.html')]
        if len(urls) % 2 == 0:
            artifact_urls.extend(urls)

        else:
            job_name = ci_job['workflows']['job_name']
            logger.info(f'Incomplete Build: {job_name}')

    return artifact_urls


def build_notebook_sources(artifact_urls: typing.List[str], merge_context: MergeContext) -> types.GeneratorType:
    notebook_sources: typing.List[NotebookSource] = []
    for url in artifact_urls:
        filename = os.path.basename(url)
        filepath = os.path.join(merge_context.artifact_dest_dir, filename)
        file_category = os.path.dirname(url).rsplit('/', 1)[-1]
        file_collection = os.path.dirname(url).rsplit('/', 2)[-2]
        meta_file = filename.endswith('metadata.json')
        resp = requests.get(url, auth=CircleCIAuth(), stream=True)
        logger.info(f'Storing File[{filepath}]')
        with open(filepath, 'wb') as stream:
            for content in resp.iter_content(chunk_size=1024):
                stream.write(content)

        yield NotebookSource(filename, filepath, file_category, file_collection, url, meta_file)


def latest_artifacts_from_jobs(command_context: CICommandContext,
                               merge_context: MergeContext,
                               existing_categories: typing.List[str]) -> types.GeneratorType:
    for job in find_build_jobs(command_context.project_path,
                               command_context.collection_names,
                               command_context.category_names,
                               command_context.notebook_names):

        namespace = '.'.join([job.collection.name, job.category.name])
        if namespace in existing_categories:
            continue

        for notebook in job.category.notebooks:
            html_filepath = '/'.join([
                merge_context.local_artifact_staging_dir,
                job.collection.name,
                job.category.name,
                f'{notebook.name}.html'])
            meta_filepath = '/'.join([
                merge_context.local_artifact_staging_dir,
                job.collection.name,
                job.category.name,
                f'{notebook.name}.metadata.json'])

            if any([
                not os.path.exists(html_filepath),
                not os.path.exists(meta_filepath)]):
                continue

            html_filename = os.path.basename(html_filepath)
            yield NotebookSource(html_filename,
                                 html_filepath,
                                 job.category.name,
                                 job.collection.name,
                                 'local-file',
                                 meta_filepath)

            meta_filename = os.path.basename(meta_filepath)
            yield NotebookSource(meta_filename,
                                 meta_filepath,
                                 job.category.name,
                                 job.collection.name,
                                 'local-file',
                                 meta_filepath)


def run_artifact_merge(command_context: CICommandContext, merge_context: MergeContext) -> types.GeneratorType:
    if command_context.mode in [CIMode.Both, CIMode.Online]:
        artifact_urls = latest_circleci_artifact_urls(merge_context)
        notebook_sources = [nb_source for nb_source in build_notebook_sources(artifact_urls, merge_context)]
        existing_categories = [item for item in set(['.'.join([nb.collection, nb.category]) for nb in notebook_sources])]

    else:
        artifact_urls = []
        notebook_sources = []
        existing_categories = []

    if command_context.mode in [CIMode.Both, CIMode.Local]:
        notebook_sources.extend([nb_source for nb_source in latest_artifacts_from_jobs(command_context, merge_context, existing_categories)])

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

                if metadata['title'] is None:
                    filename = os.path.basename(cat_source[cat_source_idx].filepath).rsplit('.', 2)[0]
                    logger.error(f'Unable to extract metadata from: {filename}')
                    metadata['title'] = filename
                    metadata['description'] = filename

                else:
                    for find, replace in NAME_ISSUES:
                        metadata['title'].replace(find, replace)

                nbs.append(ArtifactNotebook(metadata['title'], metadata, notebook.filepath, notebook.filename))

            for find, replace in NAME_ISSUES:
                cat_name = cat_name.replace(find, replace)

            cats.append(ArtifactCategory(cat_name, sorted(nbs)))

        for find, replace in NAME_ISSUES:
            coll_name = coll_name.replace(find, replace)

        artifact_collections.append(ArtifactCollection(coll_name, sorted(cats)))

    html_builder.render_index(merge_context, artifact_collections)
    html_builder.render_static_assets(merge_context.assets_dir, merge_context.site_dir)

    dest_filepaths = []
    for coll in artifact_collections:
        for cat in coll.categories:
            for notebook in cat.notebooks:
                dest_filepath = os.path.join(merge_context.site_dir, coll.name, cat.name, notebook.filename)
                for find, replace in NAME_ISSUES:
                    dest_filepath = dest_filepath.replace(find, replace)

                dest_dirpath = os.path.dirname(dest_filepath)
                if not os.path.exists(dest_dirpath):
                    os.makedirs(dest_dirpath)

                shutil.copyfile(notebook.filepath, dest_filepath)
                dest_filepaths.append(dest_filepath)

    for dest_filepath in dest_filepaths:
        html_builder.extract_cells_from_html(dest_filepath)
        html_builder.render_notebook_template(dest_filepath, merge_context)

