import logging
import os

from . import __version__
from .cli import Cli

# TODO: Roadmap:
# - revamp the CLI
# - add merging + indicate conflicts
# - add multiple layout presets
# - add tests
# - improve page layout (a tricky task)
# - automate making pdf
# - add more output customization (custom tables, namespaces)


def setup_logging():
    level = logging.WARNING

    if os.getenv('DEBUG'):
        level = logging.DEBUG

    if os.getenv('LOGLEVEL'):
        level_ = getattr(logging, os.getenv('LOGLEVEL').upper())
        if isinstance(level_, int):
            level = level_

    logging.basicConfig(
        format='%(levelname)s - %(name)s: %(message)s', level=level)


def main():
    setup_logging()
    cli = Cli(__version__)
    cli.main()


if __name__ == '__main__':
    main()
