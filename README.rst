****************************************
Bio96 --- Parse data from 96 well plates
****************************************

Many medium-throughput experiments produce data in 24-, 96-, or 384-well plate 
format.  However, it can be a challenge to keep track of which wells (e.g. A1, 
B2, etc.) correspond to which experimental conditions (e.g. genotype, drug 
concentration, replicate number, etc.).  It can also be a challenge to write 
analysis scripts flexible enough to handle the bizarre plate layouts that will 
inevitably come up as more and more experiments are run.

The `bio96` package solves these challenges by introducing a TOML-based file 
format to succinctly describe the organization of wells on plates.  The file 
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
Below are the broad steps involved in analyzing the data from a 96-well plate 
experiment.  See the `File Format`_ and `Python API`_ sections for more details 
on any of these steps.

1. Create a TOML file describing the plate layout:

   For the purpose of having an example, imagine that we are interested in 
   testing the effectiveness of penicillin against several different strains of 
   pathogenic bacteria.  To do so, we will grow each strain with 12 different 
   concentrations of penicillin, in duplicate.  We will organize our 96-well 
   plate with two rows for each strain and a different concentration of 
   penicillin in each column.
   
   The TOML file for this plate would look like::

      antibiotic = 'penicillin'

      [row.A]
        strain = "E. coli"
        replicate = 1
      [row.B]
        strain = "E. coli"
        replicate = 2
      [row.C]
        strain = "L. monocytogenes"
        replicate = 1
      [row.D]
        strain = "L. monocytogenes"
        replicate = 2
      [row.E]
        strain = "N. meningitidis"
        replicate = 1
      [row.F]
        strain = "N. meningitidis"
        replicate = 2
      [row.G]
        strain = "S. aureus"
        replicate = 1
      [row.H]
        strain = "S. aureus"
        replicate = 2

      [col.1]
        conc_ng_mL = 0
      [col.2]
        conc_ng_mL = 1
      [col.3]
        conc_ng_mL = 2
      [col.4]
        conc_ng_mL = 4
      [col.5]
        conc_ng_mL = 8
      [col.6]
        conc_ng_mL = 16
      [col.7]
        conc_ng_mL = 32
      [col.8]
        conc_ng_mL = 64
      [col.9]
        conc_ng_mL = 128
      [col.10]
        conc_ng_mL = 256
      [col.11]
        conc_ng_mL = 512
      [col.12]
        conc_ng_mL = 1024

   Note that the indentation is not significant, and is only included for 
   clarity.

2. Load the plate layout into a `pd.DataFrame` using `bio96.load()`.  The data 
   frame will contain a single row for each well, with columns for each 
   experimental condition referenced in the config file::

      >>> import bio96
      >>> conditions = bio96.load('path/to/config.toml')
      >>> conditions
         well row col  row_i  col_j  antibiotic     strain  replicate  conc_ng_mL
      0    A1   A   1      0      0  penicillin    E. coli          1           0
      1    A2   A   2      0      1  penicillin    E. coli          1           1
      2    A3   A   3      0      2  penicillin    E. coli          1           2
      3    A4   A   4      0      3  penicillin    E. coli          1           4
      4    A5   A   5      0      4  penicillin    E. coli          1           8
      ..  ...  ..  ..    ...    ...         ...        ...        ...         ...
      91   H8   H   8      7      7  penicillin  S. aureus          2          64
      92   H9   H   9      7      8  penicillin  S. aureus          2         128
      93  H10   H  10      7      9  penicillin  S. aureus          2         256
      94  H11   H  11      7     10  penicillin  S. aureus          2         512
      95  H12   H  12      7     11  penicillin  S. aureus          2        1024

3. Load your actual measurements into another data frame.

   How exactly to do this depends on the type of measurements in question and 
   the particular machine that generated them.  The only important thing is 
   that the data frame contain one or more columns that specify a well, so that 
   this data frame can be merged with the one above (see step #4).

   For example, if we were doing a plate reader assay, we might have OD600 
   measurements for each well at regular timepoints::

      >>> measurements 
         well      time   od600
      0    A1   0:00:00   0.057
      1    A1   0:05:00   0.058
      2    A1   0:10:00   0.058
      3    A1   0:15:00   0.058
      4    A1   0:20:00   0.058
      ..  ...  ........   .....
      91  H12  23:40:00   1.101
      92  H12  23:45:00   1.100
      93  H12  23:50:00   1.110
      94  H12  23:55:00   1.116
      95  H12  24:00:00   1.127

4. Merge the two data frames together, to get a single data frame linking the 
   experimental conditions to the measurements::
   
      >>> df = pd.merge(conditions, measurements, on="well")
      >>> df
         well row col  row_i  col_j  antibiotic     strain  replicate  conc_ng_mL      time   od600
      0    A1   A   1      0      0  penicillin    E. coli          1           0   0:00:00   0.057
      1    A1   A   1      0      0  penicillin    E. coli          1           0   0:05:00   0.058
      2    A1   A   1      0      0  penicillin    E. coli          1           0   0:10:00   0.058
      3    A1   A   1      0      0  penicillin    E. coli          1           0   0:15:00   0.058
      4    A1   A   1      0      0  penicillin    E. coli          1           0   0:20:00   0.058
      ..  ...  ..  ..    ...    ...         ...        ...        ...         ...  ........   .....
      91  H12   H  12      7     11  penicillin  S. aureus          2        1024  23:40:00   1.101
      92  H12   H  12      7     11  penicillin  S. aureus          2        1024  23:45:00   1.100
      93  H12   H  12      7     11  penicillin  S. aureus          2        1024  23:50:00   1.110
      94  H12   H  12      7     11  penicillin  S. aureus          2        1024  23:55:00   1.116
      95  H12   H  12      7     11  penicillin  S. aureus          2        1024  24:00:00   1.127

   Note that this step will be slightly more complicated if the two data frames 
   don't have any columns that correspond exactly, like `well` does in this 
   example.

5. Use the combined data frame to slice-and-dice the data however you need to!

File Format
===========
Coming soon.

Python API
==========
Coming soon.

