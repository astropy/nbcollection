from nbcollection_tests.ci.tools import immediate_level_repo, next_level_repo, empty_dir, git_config_file

def test__pull_request_build():
    import tempfile

    from nbcollection.ci.pull_requests.utils import pull_request_build

    url = 'https://github.com/spacetelescope/dat_pyinthesky/pull/111'
    project_path = tempfile.NamedTemporaryFile().name

    pull_request_build(url, project_path)

def test__pull_request_build__manual():
    import tempfile

    from nbcollection.ci.pull_requests.utils import pull_request_build

    url = 'https://github.com/spacetelescope/dat_pyinthesky/pull/111'
    project_path = tempfile.NamedTemporaryFile().name

    raise NotImplementedError
    # pull_request_build(url, project_path)
