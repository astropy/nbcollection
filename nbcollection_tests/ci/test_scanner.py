import os
import pytest

from nbcollection_tests.ci.tools import multi_level_ignore_repo,    \
        single_collection_repo, multi_collection_repo, single_collection_repo__immediate_categories, \
        single_collection_repo__nth_categories, quick_build_collection

def test__load_ignore_data(multi_level_ignore_repo):
    from nbcollection.ci.scanner.utils import IgnoreData, load_ignore_data, \
            DEFAULT_IGNORE_ENTRIES
    ignore_data = load_ignore_data(multi_level_ignore_repo)
    for entry in ignore_data.entries:
        assert \
                entry in DEFAULT_IGNORE_ENTRIES or \
                entry in ['zero-level', 'first-level']

    assert ignore_data.__class__ is IgnoreData
    assert len(ignore_data.entries) == 8

def test__load_ignore_data__root_level_only(multi_level_ignore_repo):
    from nbcollection.ci.scanner.utils import IgnoreData, load_ignore_data, DEFAULT_IGNORE_ENTRIES
    ignore_data = load_ignore_data(multi_level_ignore_repo, root_level_only=True)
    for entry in ignore_data.entries:
        assert \
                entry in DEFAULT_IGNORE_ENTRIES or \
                entry in ['zero-level']

    assert ignore_data.__class__ is IgnoreData
    assert len(ignore_data.entries) == 7

def test__find_collections__single(single_collection_repo):
    import os

    from nbcollection.ci.scanner.utils import find_collections

    for coll in find_collections(single_collection_repo):
        assert coll.name == 'collection_one'
        assert coll.path == os.path.join(single_collection_repo, 'collection_one')

def test__find_collections__multi(multi_collection_repo):
    import os

    from nbcollection.ci import Collection
    from nbcollection.ci.scanner.utils import find_collections

    for coll in find_collections(multi_collection_repo):
        assert coll.name in ['collection_one', 'collection_two']
        assert coll.path in [
                os.path.join(multi_collection_repo, 'collection_one'),
                os.path.join(multi_collection_repo, 'collection_two')]
        assert coll.__class__ is Collection

def test__find_categories__immediate(single_collection_repo__immediate_categories):
    from nbcollection.ci import Collection, Category
    from nbcollection.ci.scanner.utils import find_collections, find_categories

    for coll_idx, coll in enumerate(find_collections(single_collection_repo__immediate_categories)):
        assert coll.__class__ is Collection
        for cat_idx, category in enumerate(find_categories(coll)):
            assert category.__class__ is Category
            assert category.name in ['asdf_example', 'cube_fitting']


        assert cat_idx == 1

    coll_idx is 0

def test__find_categories__nth_categories(single_collection_repo__nth_categories):
    from nbcollection.ci import Collection, Category
    from nbcollection.ci.scanner.utils import find_collections, find_categories

    for coll_idx, coll in enumerate(find_collections(single_collection_repo__nth_categories)):
        assert coll.__class__ is Collection
        for cat_idx, category in enumerate(find_categories(coll)):
            assert category.__class__ is Category
            assert category.name in ['asdf_example', 'cube_fitting']

            if category.name == 'cube_fitting':
                assert category.namespaces[0].name == 'namespace_folder'

        assert cat_idx == 1

    assert coll_idx == 0

def test__find_build_jobs(single_collection_repo__nth_categories):
    from nbcollection.ci.scanner.utils import find_build_jobs
    from nbcollection.ci.datatypes import BuildJob, Requirements, PreRequirements

    for job_idx, job in enumerate(find_build_jobs(single_collection_repo__nth_categories)):
        assert job.__class__ is BuildJob 
        assert job.collection.name == 'collection_one'
        assert job.category.name in ['asdf_example', 'cube_fitting']
        assert job.category.requirements.__class__ is Requirements
        assert job.category.pre_requirements.__class__ is PreRequirements

def test__run_command():
    import shutil
    import tempfile

    from nbcollection.ci.scanner.utils import run_command

    expected_filepath = tempfile.NamedTemporaryFile().name
    assert not os.path.exists(expected_filepath)
    run_command(f'touch {expected_filepath}', None)
    assert os.path.exists(expected_filepath)
    assert os.path.isfile(expected_filepath)
    os.remove(expected_filepath)

    expected_dirpath = tempfile.NamedTemporaryFile().name
    assert not os.path.exists(expected_dirpath)
    run_command(f'mkdir -p {expected_dirpath}', None)
    assert os.path.exists(expected_dirpath)
    assert os.path.isdir(expected_dirpath)
    shutil.rmtree(expected_dirpath)
    
def test__generate_job_context(single_collection_repo__nth_categories):
    from nbcollection.ci.scanner.utils import find_build_jobs, generate_job_context
    from nbcollection.ci.datatypes import Requirements, PreRequirements, PreInstall

    for job_idx, job in enumerate(find_build_jobs(single_collection_repo__nth_categories)):
        job_context = generate_job_context(job)
        assert os.path.exists(job_context.build_dir)
        assert os.path.isdir(job_context.build_dir)
        assert os.path.exists(job_context.requirements.path)
        assert job_context.requirements.__class__ == Requirements
        assert job_context.pre_requirements.__class__ == PreRequirements
        assert job_context.pre_install.__class__ == PreInstall
        for build_script in job_context.build_scripts:
            assert os.path.exists(build_script)

    assert job_idx == 1

def test__run_job_context(quick_build_collection):
    from nbcollection.ci.constants import SCANNER_BUILD_LOG_DIR, SCANNER_BUILD_DIR
    from nbcollection.ci.scanner.utils import run_job_context, generate_job_context, find_build_jobs

    for job_idx, job in enumerate(find_build_jobs(quick_build_collection)):
        job_context = generate_job_context(job)
        run_job_context(job_context)
        stdout_log = os.path.join(SCANNER_BUILD_LOG_DIR, f'{job.collection.name}-{job.category.name}.stdout')
        assert os.path.exists(stdout_log)

        stderr_log = os.path.join(SCANNER_BUILD_LOG_DIR, f'{job.collection.name}-{job.category.name}.stderr')
        assert os.path.exists(stderr_log)

        venv_dirpath = os.path.join(SCANNER_BUILD_DIR, 'venv')
        assert os.path.exists(venv_dirpath)
        assert os.path.isdir(venv_dirpath)
        import pdb; pdb.set_trace()
        pass
