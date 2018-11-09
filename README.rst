****************************************
Bio96 --- Parse data from 96 well plates
****************************************

Many medium-throughput experiments produce data in 24-, 96-, or 384-well plate 
format.  However, it can be a challenge to keep track of which wells (e.g. A1, 
B2, etc.) correspond to which experimental conditions (e.g.  genotype, drug 
concentration, replicate number, etc.).  It can also be a challenge to write 
analysis scripts to handle the bizarre plate layouts that will inevitably come 
up as more and more experiments are run.

The `bio96` package solves these challenges by introducing a TOML-based file 
format that succinctly describes the organization of wells on plates.  The file 
format is designed to be human-readable and -writable, so it can serve as a 
standalone digital record.  The file format can also parsed by `bio96` to help 
write analysis scripts that will work regardless of how you (or your 
collaborators) organize your wells on your plates.

.. image:: https://img.shields.io/pypi/v/bio96.svg
   :target: https://pypi.python.org/pypi/bio96

.. image:: https://img.shields.io/pypi/pyversions/bio96.svg
   :target: https://pypi.python.org/pypi/bio96

.. image:: https://img.shields.io/travis/kalekundert/bio96.svg
   :target: https://travis-ci.org/kalekundert/bio96

.. image:: https://img.shields.io/coveralls/kalekundert/bio96.svg
   :target: https://coveralls.io/github/kalekundert/bio96?branch=master

Installation
============
`bio96` can be installed from pip::

   $ pip install bio96

Example Usage
=============
Coming soon.

File Format
===========
Coming soon.

Python API
==========
Coming soon.

