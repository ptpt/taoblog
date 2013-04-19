#!/usr/bin/env python

from taoblog import application as app

print '----------------> Configuration <----------------'
for k,v in app.config.items():
    if k != 'SECRET_KEY':
        print '%s: %s' % (k, v)
print

app.run()
