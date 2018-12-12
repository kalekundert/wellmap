*************************************************
``bio96`` — File format for 96-well plate layouts
*************************************************

Many medium-throughput experiments produce data in 24-, 96-, or 384-well plate 
format.  However, it can be a challenge to keep track of which wells (e.g. A1, 
B2, etc.) correspond to which experimental conditions (e.g. genotype, drug 
concentration, replicate number, etc.) for large numbers of experiments.  It 
can also be a challenge to write analysis scripts flexible enough to handle the 
different plate layouts that will inevitably come up as more and more 
experiments are run.

The ``bio96`` package solves these challenges by introducing a TOML-based file 
format that succinctly describes the organization of wells on plates.  The file 
format is designed to be human-readable and -writable, so it can serve as a 
standalone digital record.  The file format can also parsed by ``bio96`` to 
help write analysis scripts that will work regardless of how you (or your 
collaborators) organize wells on your plates.

.. image:: https://img.shields.io/pypi/v/bio96.svg
   :target: https://pypi.python.org/pypi/bio96

.. image:: https://img.shields.io/pypi/pyversions/bio96.svg
   :target: https://pypi.python.org/pypi/bio96

.. image:: https://img.shields.io/travis/kalekundert/bio96.svg
   :target: https://travis-ci.org/kalekundert/bio96

.. image:: https://readthedocs.org/projects/bio96/badge/?version=latest
   :target: http://bio96.readthedocs.io/en/latest/

.. image:: https://img.shields.io/coveralls/kalekundert/bio96.svg
   :target: https://coveralls.io/github/kalekundert/bio96?branch=master

Documentation
=============
See the complete documentation `here <http://bio96.readthedocs.io/>`_.

.. image:: docs/example_usage/penicillin_resistance.svg
