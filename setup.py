#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


requires = []
for line in open('requirements.txt'):
    package = line.strip()
    if package:
        requires.append(package)


def readme():
    for file in ['README.md', 'README.rst']:
        if os.path.exists(file):
            with open('README.md') as f:
                return f.read()
    return None


setup(name='taoblog',
      version='0.0.1',
      description='A lightweight blog system',
      long_description=readme(),
      classifiers=[
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 2.7'],
      url='http://github.com/ptpt/taoblog',
      author='Tao Peng',
      author_email='ptpttt+taoblog@gmail.com',
      keywords='web,blog',
      license='MIT',
      packages=['taoblog'],
      install_requires=requires,
      include_package_data=True,
      zip_safe=False)
