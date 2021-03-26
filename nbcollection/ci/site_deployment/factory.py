import argparse
import git
import logging
import os
import shutil

from nbcollection.ci.commands.datatypes import Site

logger = logging.getLogger(__name__)


def run_site_deployment(options: argparse.Namespace) -> None:
    if not os.environ.get('CIRCLE_PULL_REQUEST', None) is None:
        logger.info('Pull Request detected. Skipping Website Publication')
        return None

    if options.site is Site.GithubPages:
        try:
            project_repo = git.Repo(options.project_path)
        except git.exc.InvalidGitRepositoryError:
            raise Exception(f'ProjectPath[{options.project_path}] does not contain a .git folder')

        current_branch = project_repo.head.reference
        try:
            branch = project_repo.heads[options.publish_branch]
        except IndexError:
            branch = project_repo.create_head(options.publish_branch)

        try:
            push_remote = project_repo.remotes[options.publish_remote]
        except IndexError:
            remote_url = os.environ['CIRCLE_REPOSITORY_URL']
            logger.info(f'Using Remote URL: {remote_url}')
            push_remote = project_repo.create_remote(options.publish_remote, remote_url)
      

        # TODO: Refactor this file traversing block to use methods available in scanner module
        project_repo.head.reference = branch
        for root, dirnames, filenames in os.walk(options.project_path):
            for dirname in dirnames:
                if dirname in ['.git', 'site'] or \
                    dirname in ['bin', 'lib', 'lib64', 'share', 'pyvenv.cfg']:  # python -m venv files
                    continue

                dirpath = os.path.join(root, dirname)
                try:
                    project_repo.index.remove(dirpath)
                except git.exc.GitCommandError:
                    pass

                shutil.rmtree(dirpath)

            for filename in filenames:
                if filename == '.gitignore':
                    continue

                filepath = os.path.join(root, filename)
                try:
                    project_repo.index.remove(filepath)
                except git.exc.GitCommandError:
                    pass

                os.remove(filepath)

            break

        for root, dirnames, filenames in os.walk(options.site_directory):
            for dirname in dirnames:
                source_dirpath = os.path.join(root, dirname)
                dest_dirpath = os.path.join(options.project_path, dirname)
                shutil.copytree(source_dirpath, dest_dirpath)

            for filename in filenames:
                source_filepath = os.path.join(root, filename)
                dest_dirpath = os.path.join(options.project_path, filename)
                shutil.copyfile(source_filepath, dest_dirpath)

            break

        shutil.rmtree(options.site_directory)
        # Force to override .gitignore
        for root, dirnames, filenames in os.walk(options.project_path):
            for dirname in dirnames:
                if dirname in ['.git', 'site'] or \
                    dirname in ['bin', 'lib', 'lib64', 'share', 'pyvenv.cfg']:  # python -m venv files
                    continue

                dirpath = os.path.join(root, dirname)
                project_repo.index.add(dirpath, force=True)

            for filename in filenames:
                filepath = os.path.join(root, filename)
                project_repo.index.add(filepath, force=True)

            break

        project_repo.index.commit('Added Site Directory Files')
        push_remote.push(options.publish_branch, force=True)

    else:
        raise NotImplementedError(options.site)


    # validate_and_parse_inputs(options)
    # command_context = CICommandContext(options.project_path,
    #                                  options.collection_names,
    #                                  options.category_names,
    #                                  options.notebook_names,
    #                                  options.ci_mode)

    # merge_context = generate_merge_context(options.project_path, options.org, options.repo_name)
    # run_artifact_merge(command_context, merge_context)
