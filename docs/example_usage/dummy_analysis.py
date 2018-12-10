#!/usr/bin/env python3

"""\
Usage:
  my_analysis_script.py <toml>
"""

import docopt
import bio96
import pandas as pd

args = docopt.docopt(__doc__)

def df_from_path(path):
   """
   Load experimental data from the given path into a data frame.  Also make 
   sure that data frame has the column(s) referenced by the `merge_cols` 
   argument to `bio96.load()`, which in this case is "Well".

   This function will generally be different for every type of data you 
   work with.  Many instruments can export data in the ``*.xlsx`` format, 
   which can be easily loaded into a data frame using ``pd.read_excel()``.  
   For other file formats, you may be able to find a library to parse them, 
   or you may have to parse them yourself.
   """
   return pd.read_excel(path)

df = bio96.load(args['<toml>'], df_from_path, {'well': 'Well'})

# The data frame loaded above will have rows for each well, columns for each
# field in the TOML file, and more columns for each kind of data found in
# the paths referenced by (or inferred from) the TOML file.  There are lots
# of ways to work with the data, but the ``pd.DataFrame.groupby()`` method
# (useful for selecting subsets of the data based on one or more attributes)
# is good to know about.

print(df)



