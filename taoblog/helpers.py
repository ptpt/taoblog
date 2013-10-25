# -*- coding: utf-8 -*-

import os
import re
import imp
import cgi
from datetime import date

from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter

# misaka is much faster
import misaka


def chinese_date(the_date):
    return u'%s月%s号' % (
        chinese_numeralize(the_date.month),
        chinese_numeralize(the_date.day))


def chinese_digitize(number):
    cardinals = [u'零', u'一', u'二', u'三', u'四', u'五', u'六', u'七', u'八', u'九']
    digits = [cardinals[int(x)] for x in str(abs(number))]
    hanzi = ''.join(digits)
    if number < 0:
        hanzi = u'负' + hanzi
    return hanzi


def chinese_numeralize(number):
    """ Translate number to chinese hanzi """
    cardinals = [u'零', u'一', u'二', u'三', u'四', u'五', u'六', u'七', u'八', u'九']
    digits = [cardinals[int(x)] for x in str(abs(number))]
    units, uc = [u'', u'十', u'百', u'千'], 4
    superunits, sc = [u'', u'万', u'亿'], 3
    hanzi = ''
    digits.reverse()
    non_zero = False
    for i, c in enumerate(digits):
        if i % uc == 0:
            if i > 0 and (i // uc) % (sc - 1) == 0:
                hanzi = superunits[-1] + hanzi
            superunit = superunits[(i // uc) % (sc - 1)]
            non_zero = False
        unit = units[i % uc] if non_zero else (units[i % uc] + superunit)
        if c == cardinals[0]:
            if non_zero and hanzi[0] != cardinals[0]:
                hanzi = cardinals[0] + hanzi
        else:
            hanzi = c + unit + hanzi
            non_zero = True
    length = len(hanzi)
    if not length:
        hanzi = cardinals[0]
    else:
        # 二百 => 两百
        hanzi = hanzi.replace(cardinals[2], u'两')
        hanzi = hanzi.replace(u'两' + units[1], cardinals[2] + units[1])
        hanzi = hanzi.replace(units[1] + u'两', units[1] + cardinals[2])
        if hanzi[-1] == u'两' and len(hanzi) > 1:
            hanzi = hanzi[:-1] + cardinals[2]
        # 一十 => 十
        if length > 1 and hanzi[0] == cardinals[1] and \
                hanzi[1] == units[1]:
            hanzi = hanzi[1:]
    if number < 0:
        hanzi = u'负' + hanzi
    return hanzi


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


def import_file(path):
    basename = os.path.basename(path)
    if basename.lower().endswith('.py'):
        name = basename[:-3]
    else:
        name = basename
    fp, path, desc = imp.find_module(name, [os.path.dirname(path)])
    try:
        return imp.load_module(name, fp, path, desc)
    finally:
        if fp:
            fp.close()


def normalize_path(*paths):
    if len(paths) > 1:
        path = os.path.join(*paths)
    else:
        path = paths[0]
    path = os.path.expanduser(path)
    path = os.path.normpath(path)
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
