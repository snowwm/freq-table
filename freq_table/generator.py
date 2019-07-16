import logging
from itertools import islice

from mako.template import Template

from . import utils

TEXT_FIELDS = ('service_type', 'affiliation', 'call_sign', 'description')
MISSING = '-'

logger = logging.getLogger(__name__)


class RecordSlice(list):
    def __init__(self, records, config):
        super().__init__(records)
        self.start_freq = self[0]['frequency']
        self.end_freq = self[-1]['frequency']
        self.caption = config['table_caption'].format(start_freq=self.start_freq,
                                                      end_freq=self.end_freq)

        logger.info('Creating slice %s:%s', self.start_freq, self.end_freq)


class RecordPage(list):
    def __init__(self, slices, number, config):
        super().__init__(slices)
        self.start_freq = self[0].start_freq
        self.end_freq = self[-1].end_freq
        self.number = number
        self.footer = config['page_footer']

        logger.info('Creating page #%i %s:%s', self.number,
                    self.start_freq, self.end_freq)


class Generator:
    def __init__(self, config):
        self.config = config

    def preprocess_record(self, r):
        logger.info('Processing record %s', r['url'])

        r['date'] = r['date'].strftime('%d.%m.%Y')

        for f in TEXT_FIELDS:
            text = r.get(f) or MISSING
            r[f] = utils.hyphenate(text)

        return r

    def split_slices(self, records):
        for slice_len in self.config['slices']:
            if slice_len == 'remainder':
                s = RecordSlice(records, self.config)
                if s:
                    yield s
                return
            else:
                yield RecordSlice(islice(records, slice_len), self.config)

    def split_pages(self, slices):
        buf = []
        n = 1

        for s in slices:
            buf.append(s)

            if (len(buf) == self.config['columns_on_page']):
                yield RecordPage(buf, n, self.config)
                buf = []
                n += 1

        if buf:
            yield RecordPage(buf, n, self.config)

    def generate_html(self, template, records):
        records = map(self.preprocess_record, records)
        slices = self.split_slices(records)
        pages = self.split_pages(slices)

        t = Template(template)
        return t.render_unicode(data=pages, **self.config)
