import logging
import os
from argparse import ArgumentParser, RawDescriptionHelpFormatter

import yaml

from .generator import Generator
from .records import RecordStore
from .scraper import Scraper

DEFAULT_CONFIG = 'build/config.yaml'
DEFAULT_TEMPLATE = 'build/output.html.mako'
DEFAULT_OUTPUT = 'build/output.html'
DEFAULT_RECORDS = 'build/records.yaml'

DESCRIPTION = """
Make printable tables from http://radioscanner.ru frequency db.

A *record* represents a frequency with associated information.
Records are identified by URL. When gathering records from multiple
sources, records with the same URl are overwritten by those processed later.

Without arguments, the program tries to load records from the default file
falling back to scraping if that's not present.
"""

logger = logging.getLogger(__name__)


class Cli:
    def __init__(self):
        self.store = RecordStore()
        parser = self.parser = ArgumentParser(
            prog='freq_table', description=DESCRIPTION,
            formatter_class=RawDescriptionHelpFormatter,
            epilog='Logs are controlled by the env var LOGLEVEL')

        parser.add_argument(
            '-s', '--scrape', action='store_true',
            help='download records from the web (before loading files)')

        parser.add_argument(
            '-u', '--update', action='store_true',
            help='scrape *after* loading files')

        parser.add_argument(
            '-n', '--no-gen', dest='gen_html', action='store_false',
            help='do not generate html output')

        parser.add_argument(
            '-l', '--load', nargs='?', const=DEFAULT_RECORDS,
            action='append', metavar='FROM_FILE',
            help='load records from a file; repeat for multiple files'
            ' (just "-l" defaults to %(const)s)')

        parser.add_argument(
            '-d', '--dump', nargs='?', const=DEFAULT_RECORDS, metavar='TO_FILE',
            help='save all gathered records to a file'
            ' (just "-d" defaults to %(const)s)')

        parser.add_argument(
            '-c', '--config', default=DEFAULT_CONFIG, metavar='CONF_FILE',
            help='config file (default: %(default)s)')

        parser.add_argument(
            '-o', '--output', default=DEFAULT_OUTPUT, metavar='OUT_FILE',
            help='output file (default: %(default)s)')

        parser.add_argument(
            '-t', '--template', default=DEFAULT_TEMPLATE, metavar='TMPL_FILE',
            help='template file (default: %(default)s)')

    def parse_args(self, args=None):
        args = self.args = self.parser.parse_args(args)

        if args.update:
            args.scrape = True

        if not args.load and not args.scrape:
            if os.path.isfile(DEFAULT_RECORDS):
                args.load = (DEFAULT_RECORDS,)
                logger.warning('Using default records file.')
            else:
                args.scrape = True
                logger.warning('No records file found, will scrape the web.')

    def main(self):
        self.load_config()

        if self.args.scrape and not self.args.update:
            self.scrape_records()

        if self.args.load:
            self.load_files()

        if self.args.update:
            self.scrape_records()

        if not self.args.dump and not self.args.gen_html:
            return

        if self.store.count() == 0:
            self.parser.error('No records to process. Aborting.')

        logger.warning('Sorting records...')
        records = self.store.get_sorted_by_freq()
        logger.warning('Sorted %i records.', len(records))

        if self.args.dump:
            self.dump_records(records)

        # and finally...
        if self.args.gen_html:
            self.gen_html(records)

        logger.warning('Done.')

    def load_config(self):
        with open(self.args.config) as fh:
            logger.warning('Loading config from %s...', fh.name)
            self.config = yaml.safe_load(fh)

    def add_records(self, records, from_):
        logger.warning('Adding records from %s...', from_)
        cnt = 0
        for r in records:
            self.store.add(r)
            cnt += 1
        logger.warning('Added %i records.', cnt)

    def scrape_records(self):
        scraper = Scraper(self.config['scraper'])
        self.add_records(scraper.get_records(),
                         from_='the web (may take a while)')

    def load_files(self):
        for file in self.args.load:
            with open(file) as fh:
                self.add_records(yaml.safe_load(fh), from_=fh.name)

    def dump_records(self, records):
        with open(self.args.dump, 'w') as fh:
            logger.warning('Writing records to %s...', fh.name)
            yaml.safe_dump(records, fh, allow_unicode=True)

    def gen_html(self, records):
        with open(self.args.template) as fh:
            logger.warning('Reading template from %s...', fh.name)
            tmpl = fh.read()

        with open(self.args.output, 'w') as fh:
            logger.warning('Generating html at %s...', fh.name)
            generator = Generator(self.config['generator'])
            html = generator.generate_html(tmpl, records)
            fh.write(html)
