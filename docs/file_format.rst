File format
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
    **path_guess** argument of the `load()` function—described in the 
    :doc:`python_api` section—can be used to provide a default path when this 
    option is not specified.  If the layout includes multiple plates (i.e. if 
    it has one or more ``[plate]`` blocks), use ``paths`` and not ``path``.  

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

  ``concat``
    A path or list of paths that should be loaded independently of this file 
    and concatenated to the resulting data frame.  Unlike ``include``, the 
    referenced paths have no effect on how this file is parsed, and are not 
    themselves affected by anything in this file.  This is useful if you want 
    to use data from multiple independent experiments in a single analysis.

  ``options``
    A block containing any options that apply to the whole layout, but not any 
    wells in particular.  For example, this would be a good place to specify 
    plotting parameters or data analysis algorithms.  The entries in this block 
    can be anything.  Thw whole block is simply parsed into a dictionary and 
    returned by the `load()` function.

  ``alert``
    A message that should be printed to the terminal every time this file is 
    loaded.  For example, if something went wrong during the experiment that 
    would affect how the data is interpreted, put that here to be reminded 
    of that every time you look at the data.

``[expt]``
   Define conditions for every well in the layout.  This can be a good place to 
   record bookkeeping information like your name, the date, the name of the 
   experiment, etc.

``[plate.NAME]``
   Define conditions for all the wells on the given plate.  NAME, which is used 
   to look up the path to the data file for the plate, can be anything.  

   Plate blocks may also include any of the blocks described below, e.g. 
   ``[plate.NAME.row.A]``.  The fields in these "nested" blocks will only apply 
   to the plate in question, and will take precedence over the same fields 
   specified outside of a plate block.

``[row.A]``
   Define conditions for all the wells in the specified row ("A" in the example 
   above).  Row must be specified as letters (upper or lower case).  If 
   necessary, rows beyond "Z" can be specified with multiple letters (e.g.  
   "AA", "AB", etc.).  You can specify multiple rows at once, e.g.  
   ``[row.'A,C,E']`` or ``[row.'A,C,...,G']``.  More details about this syntax 
   can be found below: `Specifying multiple wells`_.

``[col.1]``
   Define conditions for all the wells in the specified column ("1" in the 
   example above).  Columns must be specified using integer numbers, starting 
   from 1.  You can specify multiple columns at once, e.g. ``[col.'1,3,5']`` or 
   ``[col.'1,3,...,7']``.  More details about this syntax can be found below: 
   `Specifying multiple wells`_.

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
   Define conditions for a block of wells W columns wide, H rows tall, and with 
   the given well ("A1" in the example above) in the top-left corner.  You can 
   specify multiple blocks at once, e.g. ``[block.2x2.'A1,A3']`` or 
   ``[block.2x2.'A1,C3,...,G11']``.  More details about this syntax can be 
   found below: `Specifying multiple wells`_.

``[well.A1]``
  Define conditions for the specified well ("A1" in the example above).  You 
  can specify multiple wells at once, e.g. ``[well.'A1,A2']``.  More details 
  about this syntax can be found below: `Specifying multiple wells`_.

Specifying multiple wells
-------------------------
You can specify multiple indices for any row, column, block, or well.  This can 
often help reduce redundancy, which in turn helps reduce the chance of 
mistakes.  The basic syntax is just comma-separated indices:

=================================  =================================
Syntax                             Meaning
=================================  =================================
``[row.'A,B']``                    A, B
``[col.'1,2']``                    1, 2
``[well.'A1,A2']``                 A1, A2
=================================  =================================

Note that the quotes are necessary with this syntax because TOML doesn't allow 
unquoted keys to contain commas.

It is also possible to specify simple patterns of indices using the "ellipsis" 
syntax:

=================================  ==================================
Syntax                             Meaning
=================================  ==================================
``[row.'A,B,...,H']``              A, B, C, D, E, F, G, H
``[row.'A,C,...,G']``              A, C, E, G
``[col.'1,2,...,8']``              1, 2, 3, 4, 5, 6, 7, 8
``[col.'1,3,...,7']``              1, 3, 5, 7
``[well.'A1,A2,...,A6']``          A1, A2, A3, A4, A5, A6
``[well.'A1,C3,...,E5']``          A1, A3, A5, C1, C3, C5, E1, E3, E5
=================================  ==================================

This syntax requires exactly 4 comma-separated elements in exactly the 
following order:  the first, second, and fourth must be valid indices, and the 
third must be an ellipsis ("...").  The first index defines the start of the 
pattern, the fourth defines the end (inclusive), and the second defines the 
step size.  It is an error if you cannot get from the start to the end taking 
steps of the given size.

Note that for wells and blocks, the ellipsis pattern can propagate across both 
rows and columns.  In this case, the second index specifies the step size in 
both dimensions.  Consider the ``A1,C3,...,E5`` example from above: C3 is two 
rows and two columns away from A1, so this pattern specifies every odd well 
between A1 and E5.


