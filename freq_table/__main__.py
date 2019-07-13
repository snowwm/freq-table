import logging
import os
from argparse import ArgumentParser

import yaml

from . import utils

# TODO: write README
# TODO: switch to OO style
# TODO: auto make pdf
# TODO: add record merging
# TODO: add filters
# TODO: add more output customization
# TODO: improve page layout (a tricky task)
# TODO: inline css?

DEFAULT_CONFIG = 'build/config.yaml'
DEFAULT_TEMPLATE = 'build/output.html.mako'
DEFAULT_OUTPUT = 'build/output.html'
DEFAULT_RECORDS = 'build/records.yaml'

logger = logging.getLogger(__name__)
if os.getenv('LOGLEVEL'):
    level = getattr(logging, os.getenv('LOGLEVEL').upper())
    logging.basicConfig(level=level)


def parse_args():
    parser = ArgumentParser(
        prog='freq_table',
        description='Make printable tables from radioscanner.ru frequency db.')

    parser.add_argument('-s', '--scrape', action='store_true')
    parser.add_argument('-u', '--update', action='store_true')
    parser.add_argument('-n', '--no-gen', dest='gen_html',
                        action='store_false')
    parser.add_argument('-d', '--dump', nargs='?', const=DEFAULT_RECORDS,
                        metavar='TO_FILE')
    parser.add_argument('-l', '--load', nargs='?', const=DEFAULT_RECORDS,
                        action='append', metavar='FROM_FILE')
    parser.add_argument('-o', '--output', default=DEFAULT_OUTPUT,
                        metavar='OUT_FILE')
    parser.add_argument('-c', '--config', default=DEFAULT_CONFIG,
                        metavar='CONF_FILE')
    parser.add_argument('-t', '--template', default=DEFAULT_TEMPLATE,
                        metavar='TEMPLATE_FILE')

    args = parser.parse_args()

    if args.update:
        args.scrape = True

    if not args.load:
        if os.path.isfile(DEFAULT_RECORDS):
            args.load = (DEFAULT_RECORDS,)
            logger.warning('Using default records file.')
        else:
            args.scrape = True
            logger.warning('No records file found, will scrape the web.')

    return parser, args


def add_records(store, records, from_='the web (may take a while)'):
    logger.warning('Adding records from %s...', from_)
    cnt = 0
    for r in records:
        store[r['url']] = r
        cnt += 1
    logger.warning('Added %i records.', cnt)


def main():
    parser, args = parse_args()

    # load config
    with open(args.config) as fh:
        logger.warning('Loading config from %s...', fh.name)
        utils.config = yaml.safe_load(fh)

    # these imports use loaded config
    from . import scraper
    from . import generator
    records_by_id = {}

    # scrape records from the web
    if args.scrape and not args.update:
        add_records(records_by_id, scraper.get_records())

    # load records from files
    if args.load:
        for file in args.load:
            with open(file) as fh:
                records = yaml.safe_load(fh)
                add_records(records_by_id, records, from_=fh.name)

    # scrape overwriting loaded records
    if args.update:
        add_records(records_by_id, scraper.get_records())

    if not args.dump and not args.gen_html:
        return

    if len(records_by_id) == 0:
        parser.error('No records to process. Aborting.')

    logger.warning('Sorting records...')
    records = sorted(records_by_id.values(),
                     key=lambda r: float(r['frequency']))
    logger.warning('Sorted %i records.', len(records))

    # dump records to file
    if args.dump:
        with open(args.dump, 'w') as fh:
            logger.warning('Writing records to %s...', fh.name)
            yaml.safe_dump(records, fh, allow_unicode=True)

    # and finally...
    if args.gen_html:
        with open(args.template) as fh:
            logger.warning('Reading template from %s...', fh.name)
            tmpl = fh.read()

        with open(args.output, 'w') as fh:
            logger.warning('Generating html at %s...', fh.name)
            html = generator.generate_html(tmpl, records)
            fh.write(html)

    logger.warning('Done.')


if __name__ == '__main__':
    main()
