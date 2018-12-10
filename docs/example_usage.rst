Example usage
=============
Imagine that we are interested in testing the effectiveness of penicillin 
against eight different strains of pathogenic bacteria.  To do so, we will grow 
96-well plates with a different strain in each row and a different 
concentration of antibiotic in each column.  Furthermore, we will do the 
experiment in triplicate, with each replicate on its own plate.

The file describing these plates might look something like this:

.. literalinclude:: example_usage/penicillin_resistance.toml

We can use the ``bio96`` command-line tool to visualize the plate layout and 
make sure we correctly labeled all the wells::

   $ bio96 penicillin_resistance.toml

.. image:: example_usage/penicillin_resistance.svg

We could then parse the above TOML file (and others like it) from python:

.. literalinclude:: example_usage/dummy_analysis.py
