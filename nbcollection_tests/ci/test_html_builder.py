from nbcollection_tests.ci.tools import repo_with_html

def test_extract_cells_from_html(repo_with_html):
    import glob
    import os

    from nbcollection.ci.merge_artifacts.html_builder import extract_cells_from_html
    from nbcollection.ci.merge_artifacts.utils import generate_merge_context

    merge_context = generate_merge_context(repo_with_html, 'org-test', 'repo-test')

    for filepath in glob.glob(f'{repo_with_html}/sourced-html/*'):
        extract_cells_from_html(filepath)
        assert os.path.getsize(filepath) > 0
