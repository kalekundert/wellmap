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
    version='0.3.0',
    author='Kale Kundert',
    author_email='kale@thekunderts.net',
    description="File format for 96-well plate layouts",
    long_description=readme,
    url='https://github.com/kalekundert/bio96',
    license='MIT',
    packages=[
        'bio96',
    ],
    install_requires=[
        'pandas',
        'toml>=0.10',
        'nonstdlib>=1.12',
        'docopt',      # gui
        'matplotlib',  # gui
        'colorcet',    # gui
    ],
    extras_require={
        'docs': [
            'setuptools>=31.0.1',
            'sphinxcontrib-programoutput',
            'sphinx_rtd_theme',
        ],
    },
    entry_points={
        'console_scripts': [
            'bio96 = bio96.verify:main',
        ],
    },
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
    zip_safe=False,
    include_package_data=True,
)
