#!/usr/bin/env python3
# encoding: utf-8

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import re
with open('bio96/__init__.py') as file:
    version_pattern = re.compile("__version__ = '(.*)'")
    version = version_pattern.search(file.read()).group(1)

with open('README.rst') as file:
    readme = file.read()

setup(
    name='bio96',
    version=version,
    author='Kale Kundert',
    author_email='kale@thekunderts.net',
    description='',
    long_description=readme,
    url='https://github.com/kalekundert/bio96',
    packages=[
        'bio96',
    ],
    include_package_data=True,
    install_requires=[
        'toml',
        'pandas',
        'nonstdlib',
    ],
    license='MIT',
    zip_safe=False,
    keywords=[
        'bio96',
    ],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries',
    ],
)
