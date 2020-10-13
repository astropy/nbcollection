import os

TEMPLATE_PATHS = {
    'initial': os.path.join(os.path.dirname(__file__), 'template/nbcollection-notebook-test-repo'),
    'multi-level-ignore': os.path.join(os.path.dirname(__file__), 'template/multi-level-ignore'),
}
#             shutil.copytree(constants.CI_REPO_TEMPLATE_PATH, self.repo_path)
# CI_REPO_TEMPLATE_PATH: str = os.path.join(
#         os.path.dirname(__file__),
#         '../templates/nbcollection-notebook-test-repo')
