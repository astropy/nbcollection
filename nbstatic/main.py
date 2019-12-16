import sys
import argparse

from .commands import convert, execute

DESCRIPTION = (
    "Type `nbstatic <command> -h` for help.")
commands = {'execute': execute,
            'convert': convert}

parser = argparse.ArgumentParser(description=DESCRIPTION)
parser.add_argument("command",
                    help="The command you'd like to run. Allowed commands: "
                         f"{list(commands.keys())}")


def main():
    args = parser.parse_args(sys.argv[1:2])
    if args.command not in commands:
        parser.print_help()
        raise ValueError(f'Unrecognized command: {args.command}\n See the help '
                         'above for usage information')

    # Run the command
    commands[args.command]()


if __name__ == "__main__":
    main()
