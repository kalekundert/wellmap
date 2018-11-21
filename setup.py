#!/usr/bin/env python3
# encoding: utf-8

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

with open('README.rst') as file:
    readme = file.read()

setup(
    name='bio96',
    version='0.2.3',
    author='Kale Kundert',
    author_email='kale@thekunderts.net',
    description="File format for 96-well plate layouts",
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
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
    ],
)
