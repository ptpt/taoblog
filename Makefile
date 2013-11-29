SRC = ./taoblog
TESTS = ./tests
STATIC = $(SRC)/static
TEMPLATES = $(SRC)/templates


.PHONY: demo example clean wc tests install just-install

demo:
	python run.py

example:
	TAOBLOG_CONFIG_PATH="`pwd`/example.cfg" python run.py

clean:
	find . -name "*.pyc" -delete
	rm -r build dist taoblog.egg-info *.html

wc:
	wc `find $(SRC) -name "*.py"`
	wc `find $(TESTS) -name "*.py"`
	wc `find $(STATIC)/coffee -name "*.coffee"`
	wc `find $(STATIC)/sass -name "*.scss"`
	wc `find $(TEMPLATES) -name "*.html"`

tests:
	python -m unittest tests

just-install:
	python setup.py install

install: just-install clean
