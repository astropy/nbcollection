import argparse
import os
import sys

from nbcollection.ci.commands import install, uninstall, venv, replicate, pull_request, build_notebooks, metadata

commands = {
  'install': install,
  'uninstall': uninstall,
  'venv': venv,
  'metadata': metadata,
  'replicate': replicate,
  'pull-request': pull_request,
  'build-notebooks': build_notebooks,
}

DESCRIPTION = """Type `nbcollection-ci <command> -h` for help.

The allowed commands are:

    nbcollection-ci install
    nbcollection-ci uninstall
    nbcollection-ci env
    nbcollection-ci replicate
    nbcollection-ci pull-request
    nbcollection-ci build-notebooks
"""

def main() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
            description=DESCRIPTION,
            formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("command",
            help=f"The command you'd like to run. Allowed commands: {list(commands.keys())}")

    args = sys.argv
    options = parser.parse_args(args[1:2])
    if options.command not in commands:
        parser.print_help()
        raise ValueError(f'Unrecognized command: {options.command}\n See the '
                         'help above for usage information')

    # Run the command
    commands[options.command].convert(args)

def run_from_cli():
    sys.path.append(os.getcwd())
    main()

if __name__ == "__main__":
    main()
