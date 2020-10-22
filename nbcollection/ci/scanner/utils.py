import glob
import logging
import os
import shutil
import subprocess
import tempfile
import time
import types
import typing

from nbcollection.ci.constants import ENCODING, PROJECT_DIR, SCANNER_BUILD_DIR, SCANNER_ARTIFACT_DEST_DIR, \
        SCANNER_BUILD_LOG_DIR
from nbcollection.ci.datatypes import Collection, Category, Notebook, PreRequirements, Requirements, Namespace, \
        BuildJob, JobContext, BuildContext, Artifact, PreInstall
from nbcollection.ci.exceptions import BuildError
from nbcollection.ci.renderer import render_template

DEFAULT_IGNORE_ENTRIES = ['.gitignore', 'venv', 'env', 'virtual-env', 'virutalenv', '.ipynb_checkpoints']
STRIP_CHARS = ' \n'

logger = logging.getLogger(__name__)

class IgnoreData(typing.NamedTuple):
    entries: typing.List[str]

def load_ignore_data(start_path: str, root_level_only: bool = False) -> IgnoreData:
    entries = []
    for root, dirnames, filenames in os.walk(start_path):
        for filename in filenames:
            if filename == '.gitignore':
                filepath = os.path.join(root, filename)
                with open(filepath, 'rb') as stream:
                    entries.extend([line.strip(STRIP_CHARS) for line in stream.read().decode(ENCODING).split('\n') if line])

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

def find_categories(collection: Collection) -> types.GeneratorType:
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
            namespaces = [Namespace(space) for space in dirpath.replace(collection.path, '').strip('/').split('/')[:-1]]
            notebooks = []
            category = Category(dirname, dirpath, collection, notebooks, pre_requirements, requirements, namespaces)
            for filepath in glob.glob(f'{dirpath}/*.ipynb'):
                name = os.path.basename(filepath).rsplit('.', 1)[0]
                notebooks.append(Notebook(name, filepath))

            if len(notebooks) < 1:
                logger.warning(f'Missing Notebooks in Category[{dirpath}]')
                continue

            yield category

def find_build_jobs(start_path: str, filter_out_collections: typing.List[str] = [], filter_out_categories: typing.List[str] = []) -> types.GeneratorType:
    for collection in find_collections(start_path):
        if filter_out_collections and collection.name in filter_out_collections:
            continue

        for category in find_categories(collection):
            if filter_out_categories and category.name in filter_out_categories:
                continue

            yield BuildJob(collection, category)

def generate_job_context(job: BuildJob) -> JobContext:
    # Constants
    build_dir = os.path.join(SCANNER_BUILD_DIR, job.semantic_path())

    # Copy Build Environment
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)

    shutil.copytree(job.category.path, build_dir)

    build_context = BuildContext(build_dir, 'html')

    # Generate Build Setup Env Script
    build_setup_script = os.path.join(build_dir, 'setup-build-env.sh')
    with open(build_setup_script, 'wb') as stream:
        stream.write(render_template('setup-build-env.tmpl.sh', {
            'build_context': build_context,
        }).encode(ENCODING))

    # Generate Build Scripts
    build_scripts = []
    for notebook in sorted(job.category.notebooks):
        if not os.path.exists(build_dir):
            os.makedirs(build_dir)

        artifact_path = os.path.join(SCANNER_ARTIFACT_DEST_DIR, job.semantic_path())
        artifact = Artifact(
                os.path.dirname(artifact_path),
                f'{artifact_path}.html', f'{artifact_path}.json')

        build_script_path = os.path.join(build_dir, f'{notebook.name}-bulid.sh')
        with open(build_script_path, 'wb') as stream:
            stream.write(render_template('build.tmpl.sh', {
                'build_context': build_context,
                'artifact': artifact,
                'notebook': notebook,
            }).encode(ENCODING))

        build_scripts.append(build_script_path)

    requirements = Requirements(os.path.join(build_dir, 'requirements.txt'))
    pre_requirements = PreRequirements(os.path.join(build_dir, 'pre-requirements.txt'))
    pre_install = PreInstall(os.path.join(build_dir, 'pre-install.sh'))
    logfile_name = f'{job.collection.name}-{job.category.name}'
    return JobContext(build_dir, build_setup_script, build_scripts, job, pre_install, pre_requirements, requirements, logfile_name)

def run_command(cmd: typing.Union[str, typing.List[str]], log_filename: str) -> None:
    if isinstance(cmd, str):
        cmd = [cmd]

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
    proc = subprocess.Popen(cmd, shell=True, stdout=stdout_file_like_object, stderr=stderr_file_like_object)

    while proc.poll() is None:
        time.sleep(.1)

    if proc.poll() > 0:
        raise BuildError(f'Process Exit Code[{proc.poll()}]. CMD: [{" ".join(cmd)}]')

def run_job_context(context: JobContext) -> None:
    run_command(f'bash {context.setup_script}', context.logfile_name)
    for build_script_filepath in context.build_scripts:
        script_filename = os.path.basename(build_script_filepath)
        build_script_log_filename = f'{context.logfile_name}-{script_filename}'
        run_command(f'bash {build_script_filepath}', build_script_log_filename)
