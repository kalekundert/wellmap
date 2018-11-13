***************************************************
``bio96`` --- File format for 96-well plate layouts
***************************************************

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

.. image:: https://img.shields.io/coveralls/kalekundert/bio96.svg
   :target: https://coveralls.io/github/kalekundert/bio96?branch=master

Installation
============
``bio96`` can be installed from ``pip``::

   $ pip install bio96

Example Usage
=============
Imagine that we are interested in testing the effectiveness of penicillin 
against eight different strains of pathogenic bacteria.  To do so, we will grow 
96-well plates with a different strain in each row and a different 
concentration of antibiotic in each column.  Furthermore, we will do the 
experiment in triplicate, with each replicate on it's own plate.

The file describing this plate might look something like this::

   # The `[meta]` block contains various options affecting how the file is
   # parsed.  In this case, the `paths` option describes where to find the
   # actual data files associated with these plates.

   [meta]
      paths = '20180704_penicillin_resistance_{}.xlsx'

   # Fields outside of any block apply to every well.  This can be a useful way 
   # to document basic information about your experiments, like who did them, 
   # what date they were done on, etc.

   antibiotic = 'penicillin'

   # The `[plate]`, `[row]`, and `[col]` blocks specify which conditions are
   # being tested in which wells.  The fields within these blocks (e.g.
   # `replicate`, `strain`, `conc_ng_mL`) can be anything.  If your plates
   # aren't organized by row and column, there are other ways to define the
   # plate layout; see the "File Format" section for more details.

   [plate.rep1]
      replicate = 1
   [plate.rep2]
      replicate = 2
   [plate.rep3]
      replicate = 3

   [row.A]
     strain = "E. coli"
   [row.B]
     strain = "K. pneumoniae"
   [row.C]
     strain = "L. monocytogenes"
   [row.D]
     strain = "M. abscessus"
   [row.E]
     strain = "M. tuberculosis"
   [row.F]
     strain = "N. meningitidis"
   [row.G]
     strain = "P. aeruginosa"
   [row.H]
     strain = "S. aureus"

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

We could then parse this file (and others like it) from python::

   #!/usr/bin/env python3

   """\
   Usage:
      my_analysis_script.py <toml>
   """

   import docopt
   import bio96

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

File Format
===========
The file format is based on TOML, so refer to the `TOML documentation 
<https://github.com/toml-lang/toml>`_ for a complete description of the basic 
syntax.  The blocks listed in this section identify wells in your experimental 
layout.  Any ``key = value`` tags within those blocks are assumed to describe 
the experimental conditions within those wells.  These tags can be anything, 
and are included as columns in the data frame returned by ``load()``.

``[meta]``
  Miscellaneous fields that affect how ``bio96`` parses the file.  This is the 
  only block that does not describe the organization of any wells.

  .. note::
      All paths specified in this section can either be absolute (if they begin 
      with a '/') or relative (if they don't).  Relative paths are considered 
      relative to the directory containing the TOML file itself, regardless of 
      what the current working directory is.

  ``path``
    The path to the file containing the actual data for this layout.  The 
    ``path_guess`` argument of the ``load()`` function—described in the `Python 
    API`_ section—can be used to provide a default path when this option is not 
    specified.  If the layout includes multiple plates (i.e. if it has one or 
    more ``[plate]`` blocks), use ``paths`` and not ``path``.  

  ``paths``
    The paths to the files containing the actual data for each plate described 
    in the layout.  You can specify these paths either as a format string or a 
    mapping:

    - Format string: The "{}" will be replaced with the name of the plate 
      (e.g. "NAME" for ``[plate.NAME]``)::

       [meta]
       paths = 'path/to/file_{}.dat'

    - Mapping: Plate names (e.g. "NAME" for ``[plate.NAME]``) are mapped to 
      paths.  This is more verbose, but more flexible than the format string 
      approach::

       [meta.paths]
       a = 'path/to/file_a.dat'
       b = 'path/to/file_b.dat'

    If the layout doesn't explicitly define any plates (i.e. if it has no 
    ``[plate]`` blocks), use ``path`` and not ``paths``.

  ``include``
    A path or a list of paths to TOML files that should provide the defaults 
    for this file.  If a list of paths is given, the later files will take 
    precedence over the earlier files.  This is useful if you want to share the 
    same basic plate layout between multiple experiments, but want to specify 
    different paths or tweak certain wells for each one.

  ``alert``
    A message that should be printed to the terminal every time this file is 
    loaded.  For example, if something went wrong during the experiment that 
    would affect how the data is interpreted, put that here to be reminded 
    of that every time you look at the data.

``[plate.NAME]``
   Define conditions for all the wells on the given plate.  The plate NAME, 
   which is used to look up the path to the data file for the plate, can 
   be anything.  

   Plate blocks may also include any of the blocks described below, e.g. 
   ``[plate.NAME.row.A]``.  The fields in these "nested" blocks will only apply 
   to the plate in question, and will take precedence over the same fields 
   specified outside of a plate block.

``[row.A]``
   Define conditions for all the wells in the specified row ("A" in the example 
   above).  Rows must be specified using uppercase letters.  Currently, rows 
   beyond "Z" are not supported.

``[col.1]``
   Define conditions for all the wells in the specified column ("1" in the 
   example above).  Rows must be specified using integer numbers, starting from 
   1.

``[irow.A]``
   Similar to ``[row.A]``, but "interleaved" with the row above or below it.  
   For example, below are the wells that would be included in the first four 
   columns of various different rows:

   - ``[row.A]``: A1, A2, A3, A4
   - ``[row.B]``: B1, B2, B3, B4
   - ``[irow.A]``: A1, B2, A3, B4
   - ``[irow.B]``: B1, A2, B3, A4

   Note that on the even columns, ``[irow.A]`` alternates "down" while 
   ``[irow.B]`` alternates "up".  In this fashion, A interleaves with 
   B, while C would interleave with D, etc.

``[icol.1]``
   Similar to ``[col.1]``, but "interleaved" with the column to the left or 
   right of it.  For example, below are the wells that would be included in the 
   first four rows of various different columns:

   - ``[col.1]``: A1, B1, A1, A1
   - ``[col.2]``: A2, B2, C2, D2
   - ``[icol.1]``: A1, B2, C1, D2
   - ``[icol.2]``: A2, B1, C2, D1

   Note that on the even rows (B/D/F/H), ``[icol.1]`` alternates "right" while 
   ``[irow.2]`` alternates "left".  In this fashion, 1 interleaves with 2, 
   while 3 would interleave with 4, etc.

``[block.WxH.A1]``
   Define conditions for a block of wells W wells wide, H columns tall, and 
   with the given well ("A1" in the example above) in the top-left corner.

``[well.A1]``
  Define conditions for the specified well ("A1" in the example above).

Python API
==========
``bio96.load(toml_path, data_loader=None, merge_cols=None, path_guess=None, path_required=False)``
   Parse the given TOML file and return a ``pd.DataFrame`` with a row for each 
   well and a column for each experimental condition specified in that file.  
   If the ``data_loader`` and ``merge_cols`` arguments are provided, that data 
   frame will also contain columns for any data associated with each well.

   **Arguments:**
   
   ``toml_path``
      The path to a file describing the layout of one or more plates.  See the 
      `File Format`_ section for details about this file.

   ``data_loader``
      A function that takes a path to a data file, parses it, and returns a 
      data frame containing the parsed data.  Note that specifying this option 
      implies ``path_required=True``.

   ``merge_cols``
      A dictionary mapping the data frame columns which identify wells between 
      the TOML file and the data files.

      The data frame loaded from the TOML file has 7 columns which identify the 
      wells (``plate``, ``path``, ``well``, ``row``, ``col``, ``row_i``, 
      ``row_j``, see the "Returns" section below for more details).  Each key 
      in this mapping must be one of these columns, but the ``path`` column is 
      implied and does not need to be specified.

      The data frame loaded from the data files will have whatever columns were 
      created by ``data_loader()``.  Each value in this mapping must be one of 
      these columns.  Furthermore, each key-value pair in this mapping must 
      associate two columns that are exactly comparable (e.g. not "A1" and 
      "A01"), or the merge will fail.  It is the responsibility of 
      ``data_loader()`` to create columns that can be merged in this manner.

   ``path_guess``
      A string specifying the where to look for a data file if none is 
      specified in the given TOML file (i.e. a default value for ``[meta] 
      path``).  This path is interpreted relative to the TOML file itself (if 
      it's not an absolute path) and is formatted with a ``pathlib.Path`` 
      representing said TOML file (e.g. ``path_guess.format(Path(toml_path))``), 
      so a typical value would be something like ``'{0.stem}.xlsx``.

   ``path_required``
      A boolean indicating whether or not the given TOML file must reference 
      one or more data files.  

   **Returns:**
   
   - If neither ``data_loader`` nor ``merge_cols`` was provided:

     A data frame containing the information about the plate layout parsed from 
     the given TOML file.  The data frame will have a row for each well and a 
     column for each experimental condition.  In addition, there will be 
     several columns identifying each well:

     - ``plate``: The name of the plate for this well.  This column will not be 
       present if there are no ``[plate]`` blocks in the TOML file.
     - ``path``: The path to the data file associated with the plate for this 
       well.  This column will not be present if no data files were referenced 
       by the TOML file.
     - ``well``: The name of the well, e.g. "A1".
     - ``row``: The name of the row for this well, e.g. "A".
     - ``col``: The name of the column for this well, e.g. "1".
     - ``row_i``: The row-index of this well, counting from 0.
     - ``col_j``: The column-index of this well, counting from 0.

   - If ``data_loader`` but not ``merge_cols`` was provided:

     Two data frames.  The first is identical to the one described for the 
     above condition.  The second is the concatenated result of calling 
     ``data_loader()`` on every path specified by the TOML file.

   - If ``data_loader`` and ``merge_cols`` were both provided:

     A single data frame with one or more rows for each well (more is possible 
     if there are multiple data points per well, e.g. a time course), a column 
     for each experimental condition described in the TOML file, and a column 
     for each kind of data loaded from the data files.  This is exactly the two 
     data frames from above, merged into one using ``pd.merge()`` along the 
     columns specified in the ``merge_cols`` argument.

Contributing
============
`Bug reports <https://github.com/kalekundert/bio96/issues>`_ and `pull requests 
<https://github.com/kalekundert/bio96/pulls>`_ are always welcome!
