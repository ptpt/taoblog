# -*- coding: utf-8 -*-

NAME = u'中文'
FALLBACK = 'en'

LOCALE = {
    'archive'    : u'存档',
    'admin'      : u'管理',
    'home'       : u'首页',
    'my account' : u'我的帐号',
    'login'      : u'登录',
    'logout'     : u'注销',

    'previous page': u'之前',
    'next page': u'之后',

    
    'posts tagged with [tags]': u'与&nbsp;'
    '{%- for tag in tags -%}'
    '{%- if not loop.first -%}'
    '{%- if loop.last -%}'
    u'&nbsp;和&nbsp;'
    '{%- else -%}'
    ',&nbsp;'
    '{%- endif -%}'
    '{%- endif -%}'
    '<span>{{ tag|e }}</span>'
    '{%- endfor -%}'
    u'&nbsp;相关的文章',

    'tagged with [tags]': u'分类在&nbsp;'
    '{%- for tag in tags -%}'
    '{%- if not loop.first -%}'
    '{%- if loop.last -%}'
    u'&nbsp;和&nbsp;'
    '{%- else -%}'
    ',&nbsp;'
    '{%- endif -%}'
    '{%- endif -%}'
    '<a href="{{ url_for(\'post.render_posts\', tags=tag) }}">{{ tag|e }}</a>'
    u'{%- endfor -%}&nbsp;下',

    'posted on [date]': u'发表于&nbsp;{{ date }}',

    'edit or delete [post]': '<form>'
    u'你可以'
    u'&nbsp;<button type="submit" class="text-link" formaction="{{ url_for(\'post.edit_post\', post_id=post.id) }}">编辑</button>&nbsp;'
    u'或者'
    u'&nbsp;<button type="submit" class="text-link" formaction="{{ url_for(\'post.delete_post\', post_id=post.id) }}" formmethod="POST" data-next="{{ url_for(\'post.render_posts\') }}">删除</button>&nbsp;'
    u'这篇文章'
    '</form'}
