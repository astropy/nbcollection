import logging
import os
import signal
import subprocess  # nosec
import time

from nbcollection.ci.constants import ENCODING
from nbcollection.ci.datatypes import BuildJob
from nbcollection.ci.scanner.utils import run_command

logger = logging.getLogger(__name__)


def enable(build_job: BuildJob, repo_info, pr_info) -> None:
    install_script = f'''#!/usr/bin/env python
cd {repo_info.repo.working_dir}
virtualenv -p /home/jbcurtin/.pyenv/shims/python venv
source venv/bin/activate
if [ -f "{build_job.category.pre_install.path}" ]; then
    bash {build_job.category.pre_install.path}
fi
if [ -f "{build_job.category.pre_requirements.path}" ]; then
    pip install -r {build_job.category.pre_requirements.path}
fi
pip install -r {build_job.category.requirements.path}
pip install -U jupyterlab
cd -
exit 0
'''
    install_script_path = os.path.join(repo_info.repo.working_dir, 'install-venv.sh')
    with open(install_script_path, 'wb') as stream:
        stream.write(install_script.encode(ENCODING))

    run_command(f'bash {install_script_path}', 'replicate')
    run_script = f'''#!/usr/bin/env python
cd {build_job.category.path}
source {repo_info.repo.working_dir}/venv/bin/activate
jupyter-lab -y
cd -
exit 0
'''
    run_script_path = os.path.join(repo_info.repo.working_dir, 'run-venv.sh')
    with open(run_script_path, 'wb') as stream:
        stream.write(run_script.encode(ENCODING))

    proc = subprocess.Popen(f'bash {run_script_path}', shell=True)  # nosec
    try:
        while proc.poll() is None:
            time.sleep(.1)

    except KeyboardInterrupt:
        logger.info('Exiting Notebook Session')
        pass

    proc.send_signal(signal.SIGINT)
    proc.send_signal(signal.SIGINT)
    proc.communicate('y')
    proc.wait()
