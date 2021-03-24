import multiprocessing
import logging
import os
import shutil
import time
import typing

from nbcollection.ci.scanner.utils import find_build_jobs, generate_job_context, run_job_context


BUILD_LOG_DIR = '/tmp/nbcollection-ci-build-logs'

logger = logging.getLogger(__name__)


def build_artifacts_concurrently(options, jobs, artifact_paths) -> typing.Dict[str, str]:
    if os.path.exists(BUILD_LOG_DIR):
        shutil.rmtree(BUILD_LOG_DIR)


    os.makedirs(BUILD_LOG_DIR)
    def _build_category(project_path: str, collection_name: str, category_name: str) -> None:
        os.environ['CHANNEL_BUILD'] = 'true'
        for job in find_build_jobs(project_path, [collection_name], [category_name]):
            print(job.collection.name, job.category.name)
            print('Creating Job Context: ', job.collection.name, job.category.name)
            job_context = generate_job_context(job)
            print('Running Job Context: ', job.collection.name, job.category.name)
            run_job_context(job_context, False)

        del os.environ['CHANNEL_BUILD']


    job_list = []
    for job in jobs:
        job_list.append([job.collection.name, job.category.name])


    processes = []
    max_workers = options.max_workers
    logger.info(f'Job List: {len(job_list)} - Max Workers: {max_workers}')
    while len(job_list) > 0 or len(processes) > 0:
        for proc_idx, proc in enumerate([proc for proc in processes if not proc.is_alive()]):
            processes.remove(proc)

        if len(processes) >= max_workers:
            time.sleep(1)
            continue

        try:
            collection_name, category_name = job_list.pop(0)
        except IndexError:
            continue

        if len(processes) >= max_workers:
            continue

        logger.info(f'Starting new Build[{collection_name}, {category_name}]')
        proc = multiprocessing.Process(target=_build_category, args=(options.project_path, collection_name, category_name))
        proc.daemon = True
        proc.start()
        processes.append(proc)
