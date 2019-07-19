import logging
import os
import sys
from argparse import ArgumentParser, RawDescriptionHelpFormatter

import pkg_resources
import yaml

from .generator import Generator
from .records import RecordStore
from .scraper import Scraper

CONFIG_FILE = 'config.yaml'
TEMPLATE_FILE = 'output.html.mako'
DEFAULT_OUTPUT = 'output.html'
DEFAULT_RECORDS = 'records.yaml'
DEFAULT_BUILD = ''

DESCRIPTION = """
Make printable tables from http://radioscanner.ru frequency db.

With no record sources provided, the program tries to load the default file
(`records.yaml`) falling back to scraping if that's not present.

All options that take file paths resolve them relative to the build directory.
The special value "-" denotes stdin/stdout, depending on the context.
"""


class CliError(Exception):
    def __init__(self, missing_template=False):
        self.missing_template = missing_template
        super().__init__()

    def __str__(self):
        msg = str(self.__cause__ or '')
        if self.missing_template:
            msg += '\nLooks like one of the necessary build files is missing!'\
                   '\nTry running `freq_table --init` first'
        return msg


class Cli:
    def __init__(self, version=''):
        self.store = RecordStore()
        parser = self.parser = ArgumentParser(
            prog='freq_table', description=DESCRIPTION,
            formatter_class=RawDescriptionHelpFormatter,
            epilog='Logs are controlled by the env variable LOGLEVEL')

        parser.add_argument(
            '-V', '--version', action='version', version=f'%(prog)s {version}')

        parser.add_argument(
            '-i', '--init', action='store_true',
            help='initialize files in the build directory')

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
            '-o', '--output', default=DEFAULT_OUTPUT, metavar='OUT_FILE',
            help='output file (default: %(default)s)')

        parser.add_argument(
            '-b', '--build-dir', default=DEFAULT_BUILD, metavar='BUILD_DIR',
            help='directory containing config and template files;'
            ' (defaults to the current working directory)')

    def main(self):
        try:
            self.parse_args()
            self.do_work()
            print('Done.')
        except Exception as e:
            if 'DEBUG' in os.environ:
                raise e
            else:
                self.parser.error(e)

    def parse_args(self, args=None):
        args = self.args = self.parser.parse_args(args)

        if args.update:
            args.scrape = True

        if not args.load and not args.scrape:
            if os.path.isfile(self.get_path(DEFAULT_RECORDS)):
                args.load = (DEFAULT_RECORDS,)
                print('Using default records file.')
            else:
                args.scrape = True
                print('No records file found, will scrape the web.')

    def do_work(self):
        if self.args.init:
            self.init()
            return

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

        print('Sorting records...')
        records = self.store.get_sorted_by_freq()
        print(f'Sorted {len(records)} records.')

        if self.args.dump:
            self.dump_records(records)

        # and finally...
        if self.args.gen_html:
            self.gen_html(records)

    def get_path(self, path):
        return os.path.join(self.args.build_dir, path)

    def open_file(self, path, mode='r', encoding='utf-8'):
        # copy stdin/stdout, so it's safe to close
        if path == '-':
            if 'w' in mode:
                fd = os.dup(sys.stdout.fileno())
                path = '<stdout>'
            elif 'r' in mode:
                fd = os.dup(sys.stdin.fileno())
                path = '<stdin>'
            else:
                raise AssertionError(f'Invalid file open mode {mode}')

            f = open(fd, mode, encoding=encoding)

        else:
            try:
                f = open(self.get_path(path), mode, encoding=encoding)
            except FileNotFoundError as e:
                is_template = path in (CONFIG_FILE, TEMPLATE_FILE)
                raise CliError(is_template) from e

        f.name_ = path  # just `name` isn't writable :(
        return f

    def copy_template(self, name):
        if os.path.isfile(self.get_path(name)):
            print(f'File {name} already exists, keeping it')
            return False

        res = pkg_resources.resource_string(__name__, f'templates/{name}')
        with self.open_file(name, 'wb', encoding=None) as fh:
            print(f'Copying {name}')
            fh.write(res)
        return True

    def init(self):
        print('Initializing templates...')

        self.copy_template('config.yaml')

        if self.copy_template('output.html.mako'):
            self.copy_template('style.css')

    def load_config(self):
        with self.open_file(CONFIG_FILE) as fh:
            print(f'Loading config from {fh.name_}...')
            self.config = yaml.safe_load(fh)

    def add_records(self, records, from_):
        print(f'Adding records from {from_}...')
        cnt = 0
        for r in records:
            self.store.add(r)
            cnt += 1
        print(f'Added {cnt} records.')

    def scrape_records(self):
        scraper = Scraper(self.config['scraper'])
        self.add_records(scraper.get_records(),
                         from_='the web (may take a while)')

    def load_files(self):
        for file in self.args.load:
            with self.open_file(file) as fh:
                self.add_records(yaml.safe_load(fh), from_=fh.name_)

    def dump_records(self, records):
        with self.open_file(self.args.dump, 'w') as fh:
            print(f'Writing records to {fh.name_}...')
            yaml.safe_dump(records, fh, allow_unicode=True)

    def gen_html(self, records):
        with self.open_file(TEMPLATE_FILE) as fh:
            print(f'Reading template from {fh.name_}...')
            tmpl = fh.read()

        with self.open_file(self.args.output, 'w') as fh:
            print(f'Generating html at {fh.name_}...')
            generator = Generator(self.config['generator'])
            html = generator.generate_html(tmpl, records)
            fh.write(html)
