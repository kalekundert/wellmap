******************
Basic usage with R
******************

The following steps show how to get started with |wellmapr| in R:

.. make-list-from-sections::

1. Install wellmapr
===================
Install |wellmapr| from GitHub.  It's good to be aware that |wellmapr| is 
written in python and made available to R using the `reticulate`_ package.  
This detail shouldn't affect you in normal usage, but may be relevant if the 
installation doesn't go smoothly:

.. code-block:: r

  > devtools::install_github("kalekundert/wellmap", subdir="wellmapr")

2. Describe the plate layout
============================
Write a `TOML file <file_format>` describing the layout of an experiment.  For 
example, the following layout might be used for a standard curve:

.. literalinclude:: basic_usage/std_curve.toml
   :language: toml
   :caption: :download:`std_curve.toml <basic_usage/std_curve.toml>`

3. Confirm the plate layout
===========================
Confirm that the layout is correct by using |wellmapr::show()| to produce a 
visualization of the layout.  This is an important step, because it's much 
easier to spot mistakes in the visualization than in the layout file itself.

.. code-block:: r

  > wellmapr::show("std_curve.toml")

This map shows that:

- Each row is a different replicate.
- Each column is a different dilution.

.. figure:: basic_usage/std_curve_map.svg

It's also possible to create maps like this from the command line, which may be 
more convenient in some cases.  The best way to do this is to use 
`reticulate::py_config()`_ to find the path to the python installation used by 
reticulate_, then to invoke the :prog:`wellmap` command associated with that 
installation.  The alias is optional, but could be saved in your shell 
configuration to make the command easier to remember:

.. code-block:: console

  $ Rscript -e 'reticulate::py_config()'
  python:         /home/kale/.local/share/r-miniconda/envs/r-reticulate/bin/python
  libpython:      /home/kale/.local/share/r-miniconda/envs/r-reticulate/lib/libpython3.6m.so
  pythonhome:     /home/kale/.local/share/r-miniconda/envs/r-reticulate:/home/kale/.local/share/r-miniconda/envs/r-reticulate
  version:        3.6.10 | packaged by conda-forge | (default, Apr 24 2020, 16:44:11)  [GCC 7.3.0]
  numpy:          /home/kale/.local/share/r-miniconda/envs/r-reticulate/lib/python3.6/site-packages/numpy
  numpy_version:  1.18.5
  $ alias wellmap=/home/kale/.local/share/r-miniconda/envs/r-reticulate/bin/wellmap
  $ wellmap std_curve.toml

4. Prepare the data
===================
Load the data from the experiment in question into a tidy_ data frame.  Tidy 
data are easier to work with in general, and are required by |wellmapr| in 
particular.  If you aren't familiar with the concept of tidy data, `this 
article`__ is a good introduction.  The basic idea is to ensure that:

__ https://r4ds.had.co.nz/tidy-data.html

- Each variable is represented by a single column.
- Each observation is represented by a single row.

If possible, it's best to export data from the instrument that collected it 
directly to a tidy format.  When this isn't possible, though, you'll need to 
tidy the data yourself.  For example, consider the following data (which 
corresponds to the layout from above).  This is qPCR data, where a higher 
:math:`C_q` value indicates that less material is present.  The data are shaped 
like the plate itself, e.g. a row in the data for every row on the plate, and a 
column in the data for every column on the plate.  It's not uncommon for 
microplate instruments to export data in this format.

.. csv-table:: :download:`std_curve.csv <basic_usage/std_curve.csv>`
   :file: basic_usage/std_curve.csv
   :header-rows: 1

Below is the code to load this data into a tidy tibble_ with the following 
columns:

- *row*: A letter identifying a row on the microplate, e.g. A-H
- *col*: A number identifying a column on the microplate, e.g. 1-12
- *Cq*: The :math:`C_q` value measured for the identified well. 
  
.. code-block:: r

  > library(tidyverse)
  > 
  > load_cq <- function(path) {
  +   read_csv(path) %>%
  +   rename(row = Cq) %>%
  +   pivot_longer(
  +       !row,
  +       names_to = "col",
  +       values_to = "Cq",
  +   )
  + }
  > data <- load_cq("std_curve.csv")
  > data
  # A tibble: 18 x 3
     row   col      Cq
     <chr> <chr> <dbl>
   1 A     1     24.2 
   2 A     2     20.7 
   3 A     3     17.2 
   4 A     4     13.8 
   5 A     5     10.3 
   6 A     6      6.97
   7 B     1     24.2 
   8 B     2     20.8 
   9 B     3     17.2 
  10 B     4     13.8 
  11 B     5     10.4 
  12 B     6      6.87
  13 C     1     24.2 
  14 C     2     20.8 
  15 C     3     17.1 
  16 C     4     13.8 
  17 C     5     10.3 
  18 C     6      6.74

5. Label the data
=================
Use |wellmapr::load()| to associate the labels specified in the TOML file (e.g.  
the dilutions and replicates) with the experimental data (e.g. the :math:`C_q` 
values).  This process has three steps:

- Load a data frame containing the data (see above).
- Load another data frame containing the labels.
- Merge the two data frames.

For the sake of clarity and completeness, we will first show how to perform 
these steps `manually <#manual-merge>`__.  Practically, though, it's easier to 
let |wellmapr| perform them `automatically <#automatic-merge>`__.

Manual merge
------------
Use the |wellmapr::load()| function to create a tibble_ containing the 
information from the TOML file.  This data frame will have columns for each 
label we specified: *replicate*, *dilution*.  It will also have six columns 
identifying the wells in different ways: *well*, *well0*, *row*, *col*, 
*row_i*, *col_j*.  These columns are redundant, but this redundancy makes it 
easier to merge the labels with the data.  For example, if the wells are named 
"A1,A2,..." in the data, the *well* column can be used for the merge.  If the 
wells are named "A01,A02,...", the *well0* column can be used instead.  If the 
wells are named in some non-standard way, the *row_i* and *col_j* columns can 
be used to calculate an appropriate merge column.

.. code-block:: r

  > layout <- wellmapr::load("std_curve.toml")
  > layout
     well well0 row col row_i col_j replicate dilution
  1    A1   A01   A   1     0     0         1    1e+05
  2    A2   A02   A   2     0     1         1    1e+04
  3    A3   A03   A   3     0     2         1    1e+03
  4    A4   A04   A   4     0     3         1    1e+02
  5    A5   A05   A   5     0     4         1    1e+01
  6    A6   A06   A   6     0     5         1    1e+00
  7    B1   B01   B   1     1     0         2    1e+05
  8    B2   B02   B   2     1     1         2    1e+04
  9    B3   B03   B   3     1     2         2    1e+03
  10   B4   B04   B   4     1     3         2    1e+02
  11   B5   B05   B   5     1     4         2    1e+01
  12   B6   B06   B   6     1     5         2    1e+00
  13   C1   C01   C   1     2     0         3    1e+05
  14   C2   C02   C   2     2     1         3    1e+04
  15   C3   C03   C   3     2     2         3    1e+03
  16   C4   C04   C   4     2     3         3    1e+02
  17   C5   C05   C   5     2     4         3    1e+01
  18   C6   C06   C   6     2     5         3    1e+00

Use the `dplyr::inner_join()`_ function to associate the labels with the data.  
In this case, both data frames have columns named *row* and *col*, so those 
columns are automatically used for the merge (as indicated).  It is also easy 
to merge using columns with different names; see the documentation on 
`dplyr::inner_join()`_ for more information.

.. code-block:: pycon

  > inner_join(layout, data)
  Joining, by = c("row", "col")
     well well0 row col row_i col_j replicate dilution        Cq
  1    A1   A01   A   1     0     0         1    1e+05 24.180859
  2    A2   A02   A   2     0     1         1    1e+04 20.740120
  3    A3   A03   A   3     0     2         1    1e+03 17.183802
  4    A4   A04   A   4     0     3         1    1e+02 13.774300
  5    A5   A05   A   5     0     4         1    1e+01 10.294983
  6    A6   A06   A   6     0     5         1    1e+00  6.967062
  7    B1   B01   B   1     1     0         2    1e+05 24.157118
  8    B2   B02   B   2     1     1         2    1e+04 20.779703
  9    B3   B03   B   3     1     2         2    1e+03 17.171795
  10   B4   B04   B   4     1     3         2    1e+02 13.768831
  11   B5   B05   B   5     1     4         2    1e+01 10.362967
  12   B6   B06   B   6     1     5         2    1e+00  6.870273
  13   C1   C01   C   1     2     0         3    1e+05 24.238230
  14   C2   C02   C   2     2     1         3    1e+04 20.787008
  15   C3   C03   C   3     2     2         3    1e+03 17.147598
  16   C4   C04   C   4     2     3         3    1e+02 13.779314
  17   C5   C05   C   5     2     4         3    1e+01 10.292967
  18   C6   C06   C   6     2     5         3    1e+00  6.735704

Automatic merge
---------------
While it's good to understand how the labels are merged with the data, it's 
better to let |wellmapr| perform the merge for you.  Not only is this more 
succinct, it also handles some tricky corner cases behind the scenes, e.g.  
layouts with multiple data files.  

To load *and* merge the data using |wellmapr::load()|, you need to provide the 
following arguments:

- **data_loader**: A function that accepts a path to a file and returns a 
  tibble_ containing the data from that file.  Note that the function we wrote 
  in the previous section fulfills these requirements.  If the raw data are 
  tidy to begin with, it is often possible to directly use `readr::read_csv()`_ 
  or similar for this argument.

- **merge_cols**: An indication of which columns to merge.  In the snippet 
  below, ``TRUE`` means to use any columns that are shared between the two data 
  frames (e.g. that have the same name).  You can also use a dictionary to be 
  more explicit about which columns to merge on.

Here we also provide the **path_guess** argument, which specifies that the 
experimental data can be found in a CSV file with the same base name as the 
layout.  Note that this argument uses the syntax for string formatting in 
python, as described in the :doc:`API documentation <api_python>`.  It also 
would've been possible to specify the path to the CSV directly from the TOML 
file (see `meta.path`), in which case this argument would've been unnecessary.

.. code-block:: r

  > wellmapr::load(
  +     "std_curve.toml",
  +     data_loader = load_cq,
  +     merge_cols = TRUE,
  +     path_guess = "{0.stem}.csv",
  + )
     well well0 row col row_i col_j                          path replicate dilution        Cq
  0    A1   A01   A   1     0     0 <environment: 0x56501964bc60>         1    1e+05 24.180859
  1    A2   A02   A   2     0     1 <environment: 0x565019653a68>         1    1e+04 20.740120
  2    A3   A03   A   3     0     2 <environment: 0x56501965d790>         1    1e+03 17.183802
  3    A4   A04   A   4     0     3 <environment: 0x565019665598>         1    1e+02 13.774300
  4    A5   A05   A   5     0     4 <environment: 0x56501966f2c0>         1    1e+01 10.294983
  5    A6   A06   A   6     0     5 <environment: 0x565019673298>         1    1e+00  6.967062
  6    B1   B01   B   1     1     0 <environment: 0x56501967b0a0>         2    1e+05 24.157118
  7    B2   B02   B   2     1     1 <environment: 0x565019684dc8>         2    1e+04 20.779703
  8    B3   B03   B   3     1     2 <environment: 0x56501968cbd0>         2    1e+03 17.171795
  9    B4   B04   B   4     1     3 <environment: 0x5650196968f8>         2    1e+02 13.768831
  10   B5   B05   B   5     1     4 <environment: 0x56501969e700>         2    1e+01 10.362967
  11   B6   B06   B   6     1     5 <environment: 0x5650196a8428>         2    1e+00  6.870273
  12   C1   C01   C   1     2     0 <environment: 0x5650196b0230>         3    1e+05 24.238230
  13   C2   C02   C   2     2     1 <environment: 0x5650196b9f58>         3    1e+04 20.787008
  14   C3   C03   C   3     2     2 <environment: 0x5650196c3c80>         3    1e+03 17.147598
  15   C4   C04   C   4     2     3 <environment: 0x5650196cba88>         3    1e+02 13.779314
  16   C5   C05   C   5     2     4 <environment: 0x5650196d57b0>         3    1e+01 10.292967
  17   C6   C06   C   6     2     5 <environment: 0x5650196dd5b8>         3    1e+00  6.735704

6. Analyze the data
===================
Analyze the data given the connection between the labels and the data.  This 
step doesn't involve :mod:`wellmap`, but is included here for completeness.  
The example below makes a linear regression of the data in log-space:

.. literalinclude:: basic_usage/std_curve.R
   :language: r
   :caption: :download:`std_curve.R <basic_usage/std_curve.R>`

.. figure:: basic_usage/std_curve_r.svg

.. _tidy: https://www.jstatsoft.org/article/view/v059i10
.. _reticulate: https://rstudio.github.io/reticulate/
.. _tibble: https://tibble.tidyverse.org/
.. _`reticulate::py_config()`: https://rstudio.github.io/reticulate/articles/versions.html
.. _`dplyr::inner_join()`: https://dplyr.tidyverse.org/reference/join.html
.. _`readr::read_csv()`: https://readr.tidyverse.org/reference/read_delim.html

.. |wellmapr| replace:: :mod:`wellmapr <wellmap>`
.. |wellmapr::show()| replace:: :func:`wellmapr::show() <wellmap.show>`
.. |wellmapr::load()| replace:: :func:`wellmapr::load() <wellmap.load>`


