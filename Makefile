SRC = ./taoblog
STATIC = $(SRC)/static
TEMPLATES = $(SRC)/templates

REMOTE_DEST = "root@taopeng.me:/usr/local/lib/python2.7/dist-packages/taoblog"


.PHONY: example clean wc tests sync upload

demo:
	python run.py

example:
	TAOBLOG_CONFIG_PATH="`pwd`/example/config.cfg" python run.py

clean:
	find . -name "*.pyc" -delete

wc:
	wc `find $(SRC) -name "*.py"`
	wc `find $(SRC)/tests -name "*.py"`
	wc `find $(STATIC)/coffee -name "*.coffee"`
	wc `find $(STATIC)/sass -name "*.scss"`
	wc `find $(TEMPLATES) -name "*.html"`

tests:
	python -m unittest taoblog.tests

upload:
	rsync -avzL --exclude-from .syncignore taoblog/ $(REMOTE_DEST)

sync:
	rsync -avzL --exclude-from .syncignore --delete taoblog/ $(REMOTE_DEST)
