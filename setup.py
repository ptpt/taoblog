#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


def read_requirements():
    filename = 'requirements.txt'
    if os.path.isfile(filename):
        packages = [line.strip() for line in open(filename)
                    if line.strip()]
    else:
        packages = []
    return packages


def readme():
    for filename in ['README.md', 'README.rst']:
        if os.path.isfile(filename):
            with open(filename) as f:
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
      include_package_data=True,
      install_requires=read_requirements(),
      zip_safe=False)
