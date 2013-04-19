SRC = ./taoblog
STATIC = $(SRC)/static
TEMPLATES = $(SRC)/templates


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
