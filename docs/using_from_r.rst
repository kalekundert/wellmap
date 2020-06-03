******************
Basic usage with R
******************

Although :mod:`wellmap` is written in Python, it can also be used seamlessly 
from R by installing the *wellmapr* package:

.. code-block:: r

  > devtools::install_github("kalekundert/wellmap", subdir="wellmapr")

Usage in R is almost identical to usage in Python.  Below is the example from 
the `basic_usage` tutorial, translated into R:

.. code-block:: r

  > wellmapr::load(
  +     "std_curve.toml",
  +     data_loader = read.csv,
  +     merge_cols = TRUE,
  +     path_guess = "{0.stem}.csv")
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

It is also possible to visualize layouts directly from R:

.. code-block:: r

  > wellmapr::show("std_curve.toml")

.. figure:: basic_usage/std_curve_map.svg

Note that in order to use the :prog:`wellmap` command-line program described in 
the `basic_usage` tutorial, you must install :mod:`wellmap` using *pip* as 
shown in said tutorial.  Installing *wellmapr* alone will not install this 
program.
