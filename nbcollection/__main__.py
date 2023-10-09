import sys
import argparse

from .commands import convert, execute

commands = {"execute": execute, "convert": convert}

DESCRIPTION = """Type `nbcollection <command> -h` for help.

The allowed commands are:

    nbcollection execute
    nbcollection convert
"""

parser = argparse.ArgumentParser(
    description=DESCRIPTION, formatter_class=argparse.RawTextHelpFormatter
)
parser.add_argument(
    "command",
    help="The command you'd like to run. Allowed commands: " f"{list(commands.keys())}",
)


def main(args=None):
    args = args or sys.argv
    parsed = parser.parse_args(args[1:2])
    if parsed.command not in commands:
        parser.print_help()
        raise ValueError(
            f"Unrecognized command: {parsed.command}\n See the "
            "help above for usage information"
        )

    # Run the command
    commands[parsed.command](args)


if __name__ == "__main__":
    main()
