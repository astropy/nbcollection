from nbcollection_tests.ci.tools import immediate_level_repo, next_level_repo, empty_dir, git_config_file

def test__replicate():
    pass

def test__parse_url_to_remote_parts__git_github():
    from nbcollection.ci.replicate.utils import RemoteScheme, RemoteParts, RemoteScheme
    remote = 'git@github.com:owner/repo_name.git'
    parts = RemoteParts.ParseURLToRemoteParts(remote)
    assert RemoteScheme.Git is parts.scheme
    assert parts.netloc == 'github.com'
    assert parts.org == 'owner'
    assert parts.name =='repo_name'

def test__parse_url_to_remote_parts__https_github():
    from nbcollection.ci.replicate.utils import RemoteParts, RemoteScheme
    remote = 'https://github.com/owner/repo_name.git'
    parts = RemoteParts.ParseURLToRemoteParts(remote)
    assert parts.scheme is RemoteScheme.Https
    assert parts.netloc == 'github.com'
    assert parts.org == 'owner'
    assert parts.name == 'repo_name'

def test__parse_url_to_remote_parts__https_github_pull_request():
    from nbcollection.ci.replicate.utils import RemoteParts, RemoteScheme
    remote = 'https://github.com/astropy/nbcollection/pull/10'
    parts = RemoteParts.ParseURLToRemoteParts(remote)
    assert parts.scheme is RemoteScheme.Https
    assert parts.netloc == 'github.com'
    assert parts.org == 'astropy'
    assert parts.name == 'nbcollection'

def test__parse_git_config__none(empty_dir):
    import os

    from nbcollection.ci.replicate.utils import parse_git_config
    git_config_filepath = os.path.join(empty_dir, '.git/config')
    assert parse_git_config(git_config_filepath) is None

def test__parse_git_config(git_config_file):
    import os

    from nbcollection.ci.replicate.datatypes import GitConfig, GitConfigRemote, RemoteParts
    from nbcollection.ci.replicate.utils import parse_git_config

    git_config_filepath = os.path.join(git_config_file, '.git/config')
    git_config = parse_git_config(git_config_filepath)

    assert git_config.__class__ is GitConfig
    assert git_config.filepath == git_config_filepath
    assert git_config.options['repositoryformatversion'] == '0'
    assert git_config.options['filemode'] == 'true'
    assert git_config.options['bare'] == 'false'
    assert git_config.options['logallrefupdates'] == 'true'
    assert git_config.remotes[0].__class__ == GitConfigRemote
    assert git_config.remotes[0].name == 'jbcurtin'
    assert git_config.remotes[0].fetch == '+refs/heads/*:refs/remotes/jbcurtin/*'
    assert git_config.remotes[0].parts.__class__ == RemoteParts
    assert git_config.remotes[0].parts.netloc == 'github.com'
    assert git_config.remotes[0].parts.org == 'jbcurtin'
    assert git_config.remotes[0].parts.name == 'nbcollection'
    assert git_config.remotes[1].name == 'astropy'
    assert git_config.remotes[1].fetch == '+refs/heads/*:refs/remotes/astropy/*'
    assert git_config.remotes[1].parts.netloc == 'github.com'
    assert git_config.remotes[1].parts.org == 'astropy'
    assert git_config.remotes[1].parts.name == 'nbcollection'

def test__find_repo_path_by_remote__none(empty_dir):
    from nbcollection.ci.replicate.utils import find_repo_path_by_remote

    remote = 'git@github.com:astropy/nbcollection.git'
    repo_path = find_repo_path_by_remote(remote, empty_dir)
    assert repo_path is None

def test__find_repo_path_by_remote__immediate_level_repo(immediate_level_repo):
    import git
    import os

    from nbcollection.ci.replicate.utils import find_repo_path_by_remote

    folder_name = os.path.basename(immediate_level_repo)
    remote = f'git@github.com:jbcurtin/{folder_name}.git'
    repo_path = find_repo_path_by_remote(remote, immediate_level_repo)
    assert repo_path.__class__ is str
    repo = git.Repo(repo_path)
    assert repo.remotes[0].name == 'upstream'
    assert repo.remotes[0].url == f'git@github.com:jbcurtin/{folder_name}.git'

def test__find_repo_path_by_remote__next_level_repo(next_level_repo):
    import git
    import os

    from nbcollection.ci.replicate.utils import find_repo_path_by_remote

    folder_name = os.path.basename(next_level_repo)
    remote = f'git@github.com:jbcurtin/{folder_name}.git'
    repo_path = find_repo_path_by_remote(remote, next_level_repo)
    assert repo_path.__class__ is str
    repo = git.Repo(repo_path)
    assert repo.remotes[0].name == 'upstream'
    assert repo.remotes[0].url == f'git@github.com:jbcurtin/{folder_name}.git'

