import getpass
import glob
import logging
import os
import shutil
import subprocess  # nosec
import sys
import tempfile
import time
import types
import typing

from nbcollection.ci.constants import ENCODING, SCANNER_BUILD_DIR, SCANNER_ARTIFACT_DEST_DIR, SCANNER_BUILD_LOG_DIR
from nbcollection.ci.datatypes import Collection, Category, Notebook, PreRequirements, Requirements, Namespace, \
        BuildJob, JobContext, BuildContext, PreInstall, IgnoreData, NotebookContext, ArtifactContext, Metadata, \
        MetadataContext
from nbcollection.ci.exceptions import BuildError
from nbcollection.ci.metadata.utils import extract_metadata
from nbcollection.ci.renderer import render_template

DEFAULT_IGNORE_ENTRIES = ['.gitignore', 'venv', 'env', 'virtual-env', 'virutalenv', '.ipynb_checkpoints']
STRIP_CHARS = ' \n'

logger = logging.getLogger(__name__)


def load_ignore_data(start_path: str, root_level_only: bool = False) -> IgnoreData:
    entries = []
    for root, dirnames, filenames in os.walk(start_path):
        for filename in filenames:
            if filename == '.gitignore':
                filepath = os.path.join(root, filename)
                with open(filepath, 'rb') as stream:
                    entries.extend([
                                    line.strip(STRIP_CHARS)
                                    for line in stream.read().decode(ENCODING).split('\n')
                                    if line])

        if root_level_only:
            break

    entries.extend(DEFAULT_IGNORE_ENTRIES)
    return IgnoreData(entries)


def find_collections(start_path: str) -> types.GeneratorType:
    ignore_data = load_ignore_data(start_path)
    for root, dirnames, filenames in os.walk(start_path):
        for dirname in dirnames:
            if any([
                    dirname.startswith('.'),
                    dirname in ignore_data.entries]):
                continue

            c_path = os.path.join(start_path, dirname)
            yield Collection(dirname, c_path)

        break


def find_categories(collection: Collection, filter_in_notebooks: typing.List[str] = []) -> types.GeneratorType:
    ignore_data = load_ignore_data(collection.path, root_level_only=True)
    for root, dirnames, filenames in os.walk(collection.path):
        if any([
                'requirements.txt' in filenames,
                len(glob.glob('*.ipynb')) > 0]):
            continue

        for dirname in dirnames:
            if any([
                    dirname.startswith('.'),
                    dirname in ignore_data.entries]):
                continue

            dirpath = os.path.join(root, dirname)
            requirements_path = os.path.join(dirpath, 'requirements.txt')
            if not os.path.exists(requirements_path):
                continue

            requirements = Requirements(requirements_path)
            pre_requirements = PreRequirements(os.path.join(dirpath, 'pre-requirements.txt'))
            pre_install = PreInstall(os.path.join(dirpath, 'pre-install.sh'))
            namespaces = [
                Namespace(space)
                for space in dirpath.replace(collection.path, '').strip('/').split('/')[:-1]
            ]
            notebooks = []
            category = Category(dirname,
                                dirpath,
                                collection,
                                notebooks,
                                pre_install,
                                pre_requirements,
                                requirements,
                                namespaces)
            for filepath in glob.glob(f'{dirpath}/*.ipynb'):
                name = os.path.basename(filepath).rsplit('.', 1)[0]
                if len(filter_in_notebooks) == 0 or name in filter_in_notebooks:
                    metadata = Metadata(os.path.join(dirpath, f'{name}.metadata.json'))
                    notebooks.append(Notebook(name, filepath, metadata))

            if len(notebooks) < 1:
                logger.warning(f'Missing Notebooks in Category[{dirpath}]')
                continue

            yield category


def find_build_jobs(start_path: str,
                    filter_in_collections: typing.List[str] = [],
                    filter_in_categories: typing.List[str] = [],
                    filter_in_notebooks: typing.List[str] = []) -> types.GeneratorType:
    for collection in find_collections(start_path):
        if len(filter_in_collections) == 0 or collection.name in filter_in_collections:
            for category in find_categories(collection, filter_in_notebooks):
                if len(filter_in_categories) == 0 or category.name in filter_in_categories:
                    yield BuildJob(collection, category)


def find_virtualenv_binary() -> str:
    for path in os.environ['PATH']:
        for root, dirnames, filenames in os.walk(path):
            for filename in filenames:
                print(filename)
                if filename == 'virtualenv':
                    return os.path.join(path, filename)

            break


    # PyENV
    major_version = sys.version_info.major
    minor_version = sys.version_info.minor
    pyenv_bin_path = f'/Users/{getpass.getuser()}/.local/bin/virtualenv'
    if os.path.exists(pyenv_bin_path):
        virtualenv_python_path = f'/Users/{getpass.getuser()}/.local/lib/python{major_version}.{minor_version}/site-packages'
        if not virtualenv_python_path in sys.path:
            sys.path.append(virtualenv_python_path)

        return pyenv_bin_path


def generate_job_context(job: BuildJob) -> JobContext:
    # Constants
    build_dir = os.path.join(SCANNER_BUILD_DIR, job.semantic_path())

    # Copy Build Environment
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)

    shutil.copytree(job.category.path, build_dir)

    build_context = BuildContext(build_dir, 'html', find_virtualenv_binary())

    # Generate Build Setup Env Script
    build_setup_script = os.path.join(build_dir, 'setup-build-env.sh')
    with open(build_setup_script, 'wb') as stream:
        stream.write(render_template('setup-build-env.tmpl.sh', {
            'build_context': build_context,
        }).encode(ENCODING))

    # Generate Build Scripts
    notebook_contexts = []
    for notebook in sorted(job.category.notebooks):
        if not os.path.exists(build_dir):
            os.makedirs(build_dir)

        artifact_path = os.path.join(SCANNER_ARTIFACT_DEST_DIR, job.semantic_path())
        artifact = ArtifactContext(
                artifact_path,
                os.path.join(artifact_path, f'{notebook.name}.html'))
        metadata = MetadataContext(
                os.path.join(artifact_path, f'{notebook.name}.metadata.json'))

        notebook_context = NotebookContext(
            notebook,
            job.collection.name,
            job.category.name,
            os.path.join(build_dir, f'{notebook.name}.ipynb'),
            os.path.join(build_dir, f'{notebook.name}.build.sh'),
            metadata, artifact)

        with open(notebook_context.build_script_path, 'wb') as stream:
            stream.write(render_template('build.tmpl.sh', {
                'build_context': build_context,
                'notebook_context': notebook_context,
            }).encode(ENCODING))

        notebook_contexts.append(notebook_context)

    requirements = Requirements(os.path.join(build_dir, 'requirements.txt'))
    pre_requirements = PreRequirements(os.path.join(build_dir, 'pre-requirements.txt'))
    pre_install = PreInstall(os.path.join(build_dir, 'pre-install.sh'))
    logfile_name = f'{job.collection.name}-{job.category.name}'
    return JobContext(
            build_dir,
            build_setup_script,
            notebook_contexts,
            job,
            pre_install,
            pre_requirements,
            requirements,
            logfile_name)


def run_command(cmd: typing.Union[str, typing.List[str]], log_filename: str, std_logoutput: bool = False) -> None:
    if isinstance(cmd, str):
        cmd = [cmd]

    if std_logoutput is False:
        if not os.path.exists(SCANNER_BUILD_LOG_DIR):
            os.makedirs(SCANNER_BUILD_LOG_DIR)

        log_filename = log_filename or os.path.basename(tempfile.NamedTemporaryFile().name)

        stdout_filepath = f'{SCANNER_BUILD_LOG_DIR}/{log_filename}.stdout.log'
        with open(stdout_filepath, 'w') as stream:
            stream.write('')
        stdout_file_like_object = open(stdout_filepath, 'w')

        stderr_filepath = f'{SCANNER_BUILD_LOG_DIR}/{log_filename}.stderr.log'
        with open(stderr_filepath, 'w') as stream:
            stream.write('')
        stderr_file_like_object = open(stderr_filepath, 'w')

        logger.info(f'Running Command[{" ".join(cmd)}]')
        logger.info(f'Logs can be found[{SCANNER_BUILD_LOG_DIR}]/{log_filename}.*.log')
        proc = subprocess.Popen(cmd,  # nosec
                                shell=True,  # nosec
                                stdout=stdout_file_like_object,  # nosec
                                stderr=stderr_file_like_object)  # nosec

    else:
        proc = subprocess.Popen(cmd, shell=True)  # nosec

    while proc.poll() is None:
        time.sleep(.1)

    if proc.poll() > 0:
        raise BuildError(f'Process Exit Code[{proc.poll()}]. CMD: [{" ".join(cmd)}]')


def run_job_context(context: JobContext, std_logoutput: bool = False) -> None:
    logger.info(f'Setting up build environment: {context.job.collection.name}.{context.job.category.name}')
    run_command(f'bash "{context.setup_script}"', context.logfile_name, std_logoutput)
    for notebook in context.notebooks:
        logger.info(f'Extracting Metadata: {context.job.collection.name}.{context.job.category.name}')
        extract_metadata(notebook)
        logger.info(f'Building Notebook: {context.job.collection.name}.{context.job.category.name}')
        run_command(f'bash "{notebook.build_script_path}"', context.logfile_name, std_logoutput)
