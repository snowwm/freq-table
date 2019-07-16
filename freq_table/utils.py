import re
from datetime import date

from pyphen import Pyphen

HYPHEN = '\u00ad'  # soft hyphen (&shy;)
RUS_WORD = re.compile('([а-яА-Я]+)')

MONTHS_BY_NAME = {
    'янв': 1,
    'фев': 2,
    'мар': 3,
    'апр': 4,
    'мая': 5,  # correct
    'июн': 6,
    'июл': 7,
    'авг': 8,
    'сен': 9,
    'окт': 10,
    'ноя': 11,
    'дек': 12,
}

pyphen = Pyphen(lang='ru_RU')


def parse_date(date_str):
    parts = date_str.split()
    return date(
        day=int(parts[0]),
        month=MONTHS_BY_NAME[parts[1][:3].lower()],
        year=int(parts[2]),
    )


def hyphenate(text):
    """hyphenate russian words and keep other tokens intact"""

    # `split` places separators (in this case words) on odd positions
    split_text = RUS_WORD.split(text)
    converted = [
        pyphen.inserted(w, HYPHEN) if i & 1 else w
        for i, w in enumerate(split_text)
    ]

    return ''.join(converted)
