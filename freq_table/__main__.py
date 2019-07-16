import logging
import os

from .cli import Cli

# TODO: auto make pdf
# TODO: enable multiple templates
# TODO: add record merging
# TODO: add filters
# TODO: add more output customization
# TODO: improve page layout (a tricky task)
# TODO: inline css?

if __name__ == '__main__':
    if os.getenv('LOGLEVEL'):
        level = getattr(logging, os.getenv('LOGLEVEL').upper())
        logging.basicConfig(level=level)

    cli = Cli()
    cli.parse_args()
    cli.main()
