import logging
from itertools import islice

from mako.template import Template

from . import utils

TEXT_FIELDS = ('service_type', 'affiliation', 'call_sign', 'description')
MISSING = '-'

config = utils.get_config('generator')
logger = logging.getLogger(__name__)


class RecordSlice(list):
    def __init__(self, records):
        super().__init__(records)
        self.start_freq = self[0]['frequency']
        self.end_freq = self[-1]['frequency']
        logger.info('Creating slice %s:%s', self.start_freq, self.end_freq)

        self.caption = config['table_caption'].format(start_freq=self.start_freq,
                                                      end_freq=self.end_freq)


class RecordPage(list):
    def __init__(self, slices, number):
        super().__init__(slices)
        self.start_freq = self[0].start_freq
        self.end_freq = self[-1].end_freq
        self.number = number
        logger.info('Creating page #%i %s:%s', self.number,
                    self.start_freq, self.end_freq)

        self.footer = config['page_footer']


def preprocess_record(r):
    logger.info('Processing record %s', r['url'])

    r['date'] = r['date'].strftime('%d.%m.%Y')

    for f in TEXT_FIELDS:
        text = r.get(f) or MISSING
        r[f] = utils.hyphenate(text)

    return r


def split_slices(records):
    for slice_len in config['slices']:
        if slice_len == 'remainder':
            s = RecordSlice(records)
            if s:
                yield s
            return
        else:
            yield RecordSlice(islice(records, slice_len))


def split_pages(slices):
    buf = []
    n = 1

    for s in slices:
        buf.append(s)

        if (len(buf) == config['columns_on_page']):
            yield RecordPage(buf, n)
            buf = []
            n += 1

    if buf:
        yield RecordPage(buf, n)


def generate_html(template, records):
    records = map(preprocess_record, records)
    slices = split_slices(records)
    pages = split_pages(slices)

    t = Template(template)
    return t.render_unicode(data=pages, **config)
