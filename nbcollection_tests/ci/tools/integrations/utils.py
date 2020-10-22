import os
import shutil

from nbcollection_tests.ci.tools.constants import TEMPLATE_DIRECTORY
from nbcollection_tests.ci.tools.integrations.datatypes import Template

def generate_template(template: Template, dirpath: str) -> None:
    if template is Template.Initial:
        template_path = os.path.join(TEMPLATE_DIRECTORY, 'nbcollection-notebook-test-repo')
        shutil.copytree(template_path, dirpath)

    else:
        template_path = os.path.join(TEMPLATE_DIRECTORY, template.value)
        if not os.path.exists(template_path):
            raise IOError(f"Template doesn't exist: {template.value}")

        shutil.copytree(template_path, dirpath)
