# -*- coding: utf-8 -*-

NAME = 'English'

FALLBACK = 'default'

LOCALE = {
    'blog title': 'Tao Peng',

    'previous page': u'« Previous',

    'next page': u'Next »',

    'posts tagged with [tags]': '''Posts tagged with&nbsp;
{%- for tag in tags -%}
{%- if not loop.first -%}
{%- if loop.last -%}
&nbsp;and&nbsp;
{%- else -%}
,&nbsp;
{%- endif -%}
{%- endif -%}
<span>{{ tag|e }}</span>
{%- endfor -%}''',

    'tagged with [tags]': 'Tagged with&nbsp;'
    '{%- for tag in tags -%}'
    '{%- if not loop.first -%}'
    '{%- if loop.last -%}'
    '&nbsp;and&nbsp;'
    '{%- else -%}'
    ',&nbsp;'
    '{%- endif -%}'
    '{%- endif -%}'
    '<a href="{{ url_for(\'post.render_posts\', tags=tag) }}">{{ tag|e }}</a>'
    '{%- endfor -%}',

    'posted on [date]': '''Posted on
<time datetime="{{ date }}" pubdate>{{ date }}</time>
''',

    'edit or delete [post]': '''<form>You can
  <button type="submit" class="text-link" formaction="{{ url_for('post.edit_post', post_id=post.id) }}">edit</button> or
  <button type="submit" class="text-link" formaction="{{ url_for('post.delete_post', post_id=post.id) }}" formmethod="POST" data-next="{{ url_for('.render_posts') }}">delete</button> it
</form>'''
    }
