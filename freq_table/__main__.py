import logging
import os

from .cli import Cli

# TODO: Roadmap:
# - support stdin/stdout
# - revamp updating
# - add merging + indicate conflicts
# - improve page layout (a tricky task)
# - add multiple layout presets
# - automate making pdf
# - add more output customization (custom tables, namespaces)


def main():
    if os.getenv('LOGLEVEL'):
        level = getattr(logging, os.getenv('LOGLEVEL').upper())
        logging.basicConfig(level=level)

    cli = Cli()
    cli.parse_args()
    cli.main()


if __name__ == '__main__':
    main()
