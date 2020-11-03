import os
import shutil

from nbcollection_tests.ci.tools.constants import TEMPLATE_DIRECTORY
from nbcollection_tests.ci.tools.integrations.datatypes import Template
from nbcollection_tests.ci.tools.utils import run_command

def generate_template(template: Template, dirpath: str) -> None:
    if template is Template.Initial:
        template_path = os.path.join(TEMPLATE_DIRECTORY, 'nbcollection-notebook-test-repo')
        shutil.copytree(template_path, dirpath)

    elif template is Template.EmptyDirWithGitRemoteUpstream:
        owner = 'jbcurtin'
        folder_name = os.path.basename(dirpath)
        os.makedirs(dirpath)
        run_command(f'cd {dirpath} && git init')
        run_command(f'cd {dirpath} && git remote add upstream git@github.com:{owner}/{folder_name}.git')

    elif template is Template.NextDirWithGitRemoteUpstream:
        owner = 'jbcurtin'
        folder_name = os.path.basename(dirpath)
        next_dirpath = os.path.join(dirpath, folder_name)
        os.makedirs(next_dirpath)
        run_command(f'cd {next_dirpath} && git init')
        run_command(f'cd {next_dirpath} && git remote add upstream git@github.com:{owner}/{folder_name}.git')

    else:
        template_path = os.path.join(TEMPLATE_DIRECTORY, template.value)
        if not os.path.exists(template_path):
            raise IOError(f"Template doesn't exist: {template.value}")

        shutil.copytree(template_path, dirpath)
