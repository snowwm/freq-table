import itertools
import logging
import re

import requests
from bs4 import BeautifulSoup

from . import utils

ROW_TITLES = (
    ('frequency', 'Частота передачи'),
    ('date', 'Дата наблюдения'),
    ('place', 'Место наблюдения'),
    ('modulation', 'Модуляция'),
    ('signal_type', 'Тип сигнала'),
    ('service_type', 'Служба радиосвязи'),
    ('affiliation', 'Принадлежность'),
    ('call_sign', 'Позывной'),
    ('description', 'Описание'),
)

config = utils.get_config('scraper')
logger = logging.getLogger(__name__)


def get_records():
    for page in itertools.count():
        logger.info('Fetching page %i', page)
        r = requests.get(config['url'].format(page=page))
        yield from get_records_from_page(r.text)

        # dirty hack to determine the last page
        if '">&gt;&gt;' not in r.text:
            return


def get_records_from_page(text):
    soup = BeautifulSoup(text, features="html.parser")
    for row in soup.find_all('tr', class_=['tbCel1', 'tbCel2']):
        href = row.find('a')['href']

        logger.info('Fetching record %s', href)
        r = requests.get(href)
        rec = parse_record(r.text)

        rec['url'] = href
        yield rec


def parse_record(text):
    soup = BeautifulSoup(text, features="html.parser").find('body')
    record = {}

    for name, title in ROW_TITLES:
        soup = soup.find_next(string=re.compile(title)).find_next('td')
        value = soup.get_text(separator='\n', strip=True)

        if name == 'frequency':
            value = value.partition(' ')[0]  # drop the unit
        elif name == 'date':
            value = utils.parse_date(value)

        record[name] = value

    logger.debug('Parsed record: %s', record)
    return record
