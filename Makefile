SRC = ./taoblog
STATIC = $(SRC)/static
TEMPLATES = $(SRC)/templates


.PHONY: demo example clean wc tests


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
	python -m unittest tests
