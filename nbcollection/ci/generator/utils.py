import enum
import os
import typing

from nbcollection.ci.constants import ENCODING, PWN
from nbcollection.ci.generator.datatypes import RemoteScheme, RemoteParts, GitConfigRemote, GitConfigBranch, GitConfig

from urllib.parse import urlparse

def parse_git_config(filepath: str) -> GitConfig:
    if not os.path.exists(filepath):
        return None

    options = {}
    remotes = []
    branches = []
    with open(filepath, 'rb') as stream:
        latest_header_type = None
        latest_datas = []
        line_datas = stream.read().decode(ENCODING).split('\n')
        for idx, line in enumerate(line_datas):
            line = line.strip()
            if line.startswith('[') or idx + 1 == len(line_datas):
                if latest_header_type is None:
                    latest_header_type = line

                if len(latest_datas) == 0:
                    continue

                if 'core' in latest_header_type:
                    for entry in latest_datas:
                        head, tail = [item.strip() for item in entry.split('=')]
                        options[head] = tail

                elif 'remote' in latest_header_type:
                    remote_options = {}
                    for entry in latest_datas:
                        head, tail = [item.strip() for item in entry.split('=')]
                        remote_options[head] = tail

                    remote_options['name'] = latest_header_type.split('"')[1]
                    remotes.append(GitConfigRemote(remote_options['name'], RemoteParts.ParseURLToRemoteParts(remote_options['url']), remote_options['fetch']))

                elif 'branch' in latest_header_type:
                    branch_options = {}
                    for entry in latest_datas:
                        head, tail = [item.strip() for item in entry.split('=')]
                        branch_options[head] = tail

                    branch_options['name'] = latest_header_type.split('"')[1]
                    try:
                        git_remote = [remote for remote in remotes if remote.name == branch_options['remote']][0]
                    except IndexError:
                        git_remote = None

                    branches.append(GitConfigBranch(branch_options['name'], git_remote, branch_options['merge']))

                else:
                    raise NotImplementedError(latest_header_type)

                latest_header_type = line
                latest_datas = []

            else:
                latest_datas.append(line)

    return GitConfig(filepath, options, remotes, branches)

def find_repo_path_by_remote(remote: str, start_path: str) -> str:
    for root, dirnames, filenames in os.walk(start_path):
        if '.git' in dirnames:
            git_config_path = os.path.join(root, '.git', 'config')
            git_config = parse_git_config(git_config_path)
            if git_config:
                for git_remote in git_config.remotes:
                    if git_remote.is_match(remote):
                        return root

        for dirname in dirnames:
            dirpath = os.path.join(root, dirname)
            git_config_path = os.path.join(dirpath, '.git', 'config')
            git_config = parse_git_config(git_config_path)
            if git_config:
                for git_remote in git_config.remotes:
                    if git_remote.is_match(remote):
                        return dirpath

        break
