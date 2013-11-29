# -*- coding: utf-8 -*-

import os
import re
import cgi
from datetime import date

from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter

# misaka is much faster
import misaka


def get_date_range(year, month=None):
    year = int(year)
    if month is None:
        start = date(year=year, month=1, day=1)
        end = date(year=year + 1, month=1, day=1)
    else:
        month = int(month)
        start = date(year=year, month=month, day=1)
        if month == 12:
            end = date(year=year + 1, month=1, day=1)
        else:
            end = date(year=year, month=month + 1, day=1)
    return start, end


class BleepRenderer(misaka.HtmlRenderer, misaka.SmartyPants):
    def block_code(self, text, lang):
        if not lang:
            return '\n<pre><code>%s</code></pre>\n' % \
                cgi.escape(text.strip())
        lexer = get_lexer_by_name(lang, stripall=True)
        formatter = HtmlFormatter(style='colorful')
        return highlight(text, lexer, formatter)


md_renderer = misaka.Markdown(BleepRenderer(),
                              extensions=misaka.EXT_FENCED_CODE | misaka.EXT_NO_INTRA_EMPHASIS)


def markdown(text):
    if text is None:
        return None
    return md_renderer.render(text)


def validate_slug(slug):
    if not slug:
        return False
    p = re.compile(r'[\t\n\r !"#$%&\'()*\/<=>?@\[\\\]^`{|},.]+')
    return p.search(slug) is None


def slugify(text, delim=u'-'):
    p = re.compile(r'[\t\n\r !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')
    result = []
    for word in p.split(text.lower()):
        # word = word.encode('translit/long')
        if word:
            result.append(word)
    return unicode(delim.join(result))


def normalize_path(path, *paths):
    path = os.path.join(path, *paths)
    path = os.path.expanduser(path)
    path = os.path.abspath(path)
    return path


class Pagination(object):
    def __init__(self, page, more, urlmaker):
        self.page = page
        self.prev_page = page - 1 if page > 1 else None
        self.prev_url = urlmaker(self.prev_page) if self.prev_page else None
        self.next_page = page + 1 if more else None
        self.next_url = urlmaker(self.next_page) if self.next_page else None
        self.single = self.prev_page is None and self.next_page is None
