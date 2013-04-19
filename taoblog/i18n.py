import os
from jinja2 import DictLoader, Environment, TemplateNotFound

from .helpers import import_file


class I18n(object):
    def __init__(self, folder=None):
        self.locales = {}
        self.fallbacks = {}
        self.names = {}
        if folder:
            self.load(folder)

    def is_fallback(self, back, front):
        """ Determine if back locale is the fallback of front locale. """
        return back == front or (front in self.fallbacks and self.is_fallback(back, self.fallbacks[front]))
        # same as the following code
        # if back == front:
        #     return True
        # if front in self.fallbacks:
        #     return self.is_fallback(back, self.fallbacks[front])
        # return False

    def load(self, folder, silent=False):
        if silent and not os.path.isdir(folder):
            return False
        for filename in os.listdir(folder):
            path = os.path.join(folder, filename)
            if (os.path.islink(path) or os.path.isfile(path)) and filename.lower().endswith('.py'):
                id = filename[:-3].lower()
                module = import_file(path)
                if hasattr(module, 'LOCALE') and isinstance(module.LOCALE, dict):
                    self.locales[id] = self.create_jinja_environment()
                    # ignore case
                    self.locales[id].loader = DictLoader(
                        dict((k.lower(), v) for k,v in module.LOCALE.items()))
                if hasattr(module, 'NAME') and id in self.locales:
                    self.names[id] = module.NAME
                if hasattr(module, 'FALLBACK') and id in self.locales:
                    if self.is_fallback(id, module.FALLBACK):
                        raise RuntimeError('A fallback circle is found in locale file "%s"' % path)
                    else:
                        self.fallbacks[id] = module.FALLBACK
        return True

    def create_jinja_environment(self):
        return Environment()

    def localize(self, key, id, **kwargs):
        lower_key = unicode(key).lower()
        try:
            template = self.locales[id].get_template(lower_key)
        except TemplateNotFound:
            return self.localize(key, self.fallbacks[id], **kwargs)
        return template.render(**kwargs)

    def get_locale_name(self, id, default=None):
        return self.names.get(id, default)

    def get_locale_fallback(self, id, default=None):
        return self.fallbacks.get(id, default)

    def validate_fallbacks(self):
        return set(self.locales).issuperset(set(self.fallbacks.values()))
