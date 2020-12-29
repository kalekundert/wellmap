***********
File format
***********

The basic organization of a :mod:`wellmap` file is as follows: first you specify 
a group of wells, then you specify the experimental parameters associated with 
those wells.  For example, the following snippet specifies that well A1 has a 
concentration of 100:

.. code-block:: toml

  [well.A1]
  conc = 100

The file format is based on TOML, so refer to the `TOML documentation <toml>`_ 
for a complete description of the basic syntax.  Typically, square brackets 
(i.e. `tables <table>`_) are used to identify groups of wells and `key/value 
pairs <key_value>`_ are used to set the experimental parameters for those 
wells.  Note however that all of the following are equivalent:

.. code-block:: toml

  [well.A1]
  conc = 100

  [well]
  A1.conc = 100

  well.A1.conc = 100
  
Most of this document focuses on describing the various ways to succinctly 
specify different groups of wells, e.g. `[row.A]`, `[col.1]`, `[block.WxH.A1]`, 
etc.  There is no need to specify the size of the plate.  The data frame 
returned by `load()` will contain a row for each well implied by the layout 
file.

Experimental parameters can be specified by setting any `key`_ associated with 
a well group (e.g. ``conc`` in the above examples) to a scalar value (e.g.  
string_, integer_, float_, boolean_, date_, time_, etc.).  There are no 
restrictions on what these parameters can be named, although complex names 
(e.g. with spaces or punctuation) may need to be quoted.  The data frame 
returned by `load()` will contain a column named for each parameter associated 
with any well in the layout.  Not every well needs to have a value for every 
parameter; missing values will be represented in the data frame by ``nan``.

[meta]
======
Miscellaneous fields that affect how :mod:`wellmap` parses the file.  This is the 
only section that does not describe the organization of any wells.

.. note::
    All paths specified in this section can either be absolute (if they begin 
    with a '/') or relative (if they don't).  Relative paths are considered 
    relative to the directory containing the TOML file itself, regardless of 
    what the current working directory is.

meta.path
---------
The path to the file containing the actual data for this layout.  The 
**path_guess** argument of the `load()` function can be used to provide a 
default path when this option is not specified.  If the layout includes 
multiple plates (i.e. if it has one or more `[plate.NAME]` sections), use 
`meta.paths` and not `meta.path`.  

meta.paths
----------
The paths to the files containing the actual data for each plate described in 
the layout.  You can specify these paths either as a format string or a 
mapping:

- Format string: The "{}" will be replaced with the name of the plate (e.g. 
  "NAME" for ``[plate.NAME]``):

  .. code-block:: toml

    [meta]
    paths = 'path/to/file_{}.dat'

- Mapping: Plate names (e.g. "NAME" for ``[plate.NAME]``) are mapped to 
  paths.  This is more verbose, but more flexible than the format string 
  approach:

  .. code-block:: toml

    [meta.paths]
    a = 'path/to/file_a.dat'
    b = 'path/to/file_b.dat'

If the layout doesn't explicitly define any plates (i.e. if it has no 
`[plate.NAME]` sections), use `meta.path` and not `meta.paths`.

meta.include
------------
A path or a list of paths to TOML files that should provide the defaults 
for this file.  If a list of paths is given, the later files will take 
precedence over the earlier files.  This is useful if you want to share the 
same basic plate layout between multiple experiments, but want to specify 
different paths or tweak certain wells for each one.

.. rubric:: Example:

The first layout describes a generic 10-fold serial dilution.  The second 
layout expands on the first by specifying which sample is in each row.  Note 
that the first layout could not be used on its own, because it doesn't specify 
any rows:

.. example:: file_format/serial_dilution.toml file_format/meta_include.toml

  [col]
  1.conc = 1e4
  2.conc = 1e3
  3.conc = 1e2
  4.conc = 1e1
  5.conc = 1e0
  6.conc = 0

  --EOF--

  [meta]
  include = 'serial_dilution.toml'

  [row.'A,B']
  sample = 'α'

  [row.'C,D']
  sample = 'β'

meta.concat
-----------
The paths of one or more TOML files that should be loaded independently of this 
file and concatenated to the resulting data frame.  This is useful for 
combining multiple independent experiments (e.g. replicates performed on 
different days) into a single layout for analysis.  Unlike `meta.include`, the 
referenced paths have no effect on how this file is parsed, and are not 
themselves affected by anything in this file.

The paths can be specified either as a string, a list, or a dictionary.  Use a 
string to load a single path and a list to load multiple paths.  Use a 
dictionary to load multiple paths and to assign a unique plate name (its key in 
the dictionary) to each one.  Assigning plate names in this manner is useful 
when concatenating multiple single-plate layouts (as in the example below), 
because it keeps the wells from different plates easy to distinguish.  Note 
that the plate names specified via dictionary keys will override any plate 
names specified in the layouts themselves.

.. rubric:: Example:

The first two layouts describe the same experiment with different samples.  The 
third layout combines the first two for easier analysis.

.. example:: file_format/expt_1.toml file_format/expt_2.toml file_format/concat.toml

  [block.4x4.A1]
  sample = 'α'

  --EOF--

  [block.4x4.A1]
  sample = 'β'

  --EOF--

  [meta.concat]
  X = 'expt_1.toml'
  Y = 'expt_2.toml'

meta.alert
----------
A message that should be printed to the terminal every time this file is 
loaded.  For example, if something went wrong during the experiment that would 
affect how the data is interpreted, put that here to be reminded of that every 
time you look at the data.

[expt]
======
Specify parameters that apply to every well in the layout, e.g. parameters that 
aren't being varied.  These parameters are important to record for two reasons 
that may not be immediately obvious.  First, they contribute to the complete 
annotation of the experiment, which will make the experiment easier for others 
(including yourself, after a few months) to understand.  Second, they make it 
easier to write reusable analysis scripts, because the scripts can rely on 
every layout specifying every relevant parameter, not only those parameters 
that are being varied.

Avoid using this section for metadata such as your name, the date, the name of 
the experiment, etc.  While this kind of metadata does apply to every well, it 
doesn't affect how the data will be analyzed.  Including it here needlessly 
bloats the data frame returned by `load()`.  It's better to put this 
information in top-level key/value pairs (e.g. outside of any well group).  
Analysis scripts can still access this information using the **extras** 
argument to the `load()` function, but it will not clutter the data frame used 
for analysis.

Note that the :prog:`wellmap` command by default only displays experimental 
parameters that have at least two different values across the whole layout, 
which normally excludes `[expt]` parameters.  To see such a parameter anyways, 
provide its name as one of the ``<attr>`` arguments.

.. rubric:: Example:

This layout demonstrates the difference between `[expt]` parameters and 
metadata.  All of the wells on this plate have the same sample, but the sample 
is relevant to the analysis and might vary in other layouts analyzed by the 
same script.  In contrast, the name and date are just (useful) metadata.

.. example:: file_format/expt.toml
  :attrs: sample

  name = "Kale Kundert"
  date = 2020-05-26

  [expt]
  sample = 'α'

  # Without this, the plate wouldn't have any wells.
  [block.4x4.A1]

[plate.NAME]
============
Specify parameters that differ between plates.  Each plate must have a unique 
name, which will be included in the data frame returned by `load()`.  The names 
can be any valid `TOML key <key>`_.  In other words, almost any name is 
allowed, but complex names (e.g. with spaces or punctuation) may need to be 
quoted.  Note that these names are also used in `meta.paths` to associate data 
with each plate.

Any parameters specified outside of a plate will apply to all plates.  Any 
key/value pairs specified at the top-level of a plate will apply to the whole 
plate.  Any well groups specified within a plate (e.g. ``[plate.NAME.row.A]``) 
will only apply to that plate, and will take precedence over values specified 
in the same well groups (e.g. ``[row.A]``) outside the plate.  Refer to the 
`precedence rules` for more information.

.. rubric:: Example:

The following layout shows how to define parameters that apply to:

- All plates (conc).
- One specific plate (sample=α).
- Part of one specific plate (sample=β,γ).

.. example:: file_format/plate.toml
  
  [plate.X]
  sample = 'α'

  [plate.Y.block.2x4.A1]
  sample = 'β'

  [plate.Y.block.2x4.A3]
  sample = 'γ'

  [col.'1,3']
  conc = 0

  [col.'2,4']
  conc = 100

  # Without this, plate X wouldn't have any rows.
  [row.'A,B,C,D']

[row.A]
=======
Specify parameters for all the wells in the given row (e.g. "A").  Rows must be 
specified as letters, either upper- or lower-case.  If necessary, rows beyond 
"Z" can be specified with multiple letters (e.g.  "AA", "AB", etc.).  You can 
use the `pattern syntax`_ to specify multiple rows at once, e.g.  
``[row.'A,C,E']`` or ``[row.'A,C,...,G']``.

.. rubric:: Examples:

The following layout specifies a different sample for each row:

.. example:: file_format/row.toml

  [row]
  A.sample = 'α'
  B.sample = 'β'
  C.sample = 'γ'
  D.sample = 'δ'

  # Indicate how many columns there are.
  [col.'1,2,3,4']

The following layout uses the `pattern syntax`_ to specify the same sample in 
multiple rows:

.. example:: file_format/row_pattern.toml

  [row.'A,C']
  sample = 'α'

  [row.'B,D']
  sample = 'β'

  # Indicate how many columns there are.
  [col.'1,2,3,4']

[col.1]
=======
Specify parameters for all the wells in the given column (e.g. "1").  Columns 
must be specified using integer numbers, starting from 1.  You can use the 
`pattern syntax`_ to specify multiple columns at once, e.g. ``[col.'1,3,5']`` 
or ``[col.'1,3,...,7']``.

.. rubric:: Examples:

The following layout specifies a different sample for each column:

.. example:: file_format/col.toml

  [col]
  1.sample = 'α'
  2.sample = 'β'
  3.sample = 'γ'
  4.sample = 'δ'

  # Indicate how many rows there are.
  [row.'A,B,C,D']

The following layout uses the `pattern syntax`_ to specify the same sample in 
multiple columns:

.. example:: file_format/col_pattern.toml

  [col.'1,3']
  sample = 'α'

  [col.'2,4']
  sample = 'β'

  # Indicate how many rows there are.
  [row.'A,B,C,D']

[irow.A]
========
Similar to `[row.A]`, but "interleaved" with the row above or below it.  This 
layout is sometimes used for experiments that may be sensitive to neighbor 
effects or slight gradients across the plate.

.. rubric:: Example:

The following layout interleaves samples between rows.  Note that on the even 
columns, ``[irow.A]`` alternates "down" while ``[irow.B]`` alternates "up".  In 
this fashion, A interleaves with B, C interleaves with D, etc.

.. example:: file_format/irow.toml

  [irow]
  A.sample = 'α'
  B.sample = 'β'
  C.sample = 'γ'
  D.sample = 'δ'

  # Indicate how many columns there are.
  [col.'1,2,...,4']

[icol.1]
========
Similar to `[col.1]`, but "interleaved" with the column to the left or right of 
it.  This layout is sometimes used for experiments that may be sensitive to 
neighbor effects or slight gradients across the plate.

.. rubric:: Example:

The following layout interleaves samples between columns.  Note that on the 
rows columns (i.e. B/D/H/F), ``[icol.1]`` alternates "right" while ``[icol.2]`` 
alternates "left".  In this fashion, 1 interleaves with 2, 3 interleaves with 
4, etc.

.. example:: file_format/icol.toml

  [icol]
  1.sample = 'α'
  2.sample = 'β'
  3.sample = 'γ'
  4.sample = 'δ'

  # Indicate how many rows there are.
  [row.'A,B,...,D']

[block.WxH.A1]
==============
Specify parameters for a block of wells W columns wide, H rows tall, and with 
the given well (e.g. "A1") in the top-left corner.  You can use the `pattern 
syntax`_ to specify multiple blocks at once, e.g. ``[block.2x2.'A1,A5']`` or 
``[block.2x2.'A1,E5,...,E9']``.

.. rubric:: Examples:

The following layout defines blocks of various sizes, each representing a 
different sample:

.. example:: file_format/block.toml

  [block.2x2]
  A1.sample = 'α'
  A3.sample = 'β'

  [block.4x1]
  C1.sample = 'γ'
  D1.sample = 'δ'

The following layout uses the `pattern syntax`_ to specify the same sample in 
multiple blocks:

.. example:: file_format/block_pattern.toml

  [block.2x2.'A1,C3']
  sample = 'α'

  [block.2x2.'A3,C1']
  sample = 'β'

[well.A1]
=========
Specify parameters for the given well (e.g. "A1").  You can use the `pattern 
syntax`_ specify multiple wells at once, e.g. ``[well.'A1,A3']`` or 
``[well.'A1,B3,...C11']``.

.. rubric:: Examples:

The following layout specifies samples for two individual wells:

.. example:: file_format/well.toml

  [well.A1]
  sample = 'α'

  [well.D4]
  sample = 'β'

The following layout uses the `pattern syntax`_ to specify the same sample for 
multiple wells:

.. example:: file_format/well_pattern.toml
  :attrs: sample

  [well.'A1,D4,...,D4']
  sample = 'α'

Pattern syntax
==============
You can specify multiple indices for any row, column, block, or well.  This can 
often help reduce redundancy, which in turn helps reduce the chance of 
mistakes.  The following table shows some examples of this syntax:

=================================  ==================================
Syntax                             Meaning
=================================  ==================================
``[row.'A,B']``                    A, B
``[row.'A,B,...,H']``              A, B, C, D, E, F, G, H
``[row.'A,C,...,G']``              A, C, E, G
``[col.'1,2']``                    1, 2
``[col.'1,2,...,8']``              1, 2, 3, 4, 5, 6, 7, 8
``[col.'1,3,...,7']``              1, 3, 5, 7
``[well.'A1,A2']``                 A1, A2
``[well.'A1,A2,...,A6']``          A1, A2, A3, A4, A5, A6
``[well.'A1,C3,...,E5']``          A1, A3, A5, C1, C3, C5, E1, E3, E5
=================================  ==================================

The most basic form of this syntax uses commas to specify multiple positions 
for a single row, column, block, or well.  Note that the quotes are necessary 
with this syntax because TOML doesn't allow unquoted keys to contain commas.

A more advanced form of this syntax uses ellipses to specify simple patterns.  
This form requires exactly 4 comma-separated elements in exactly the following 
order:  the first, second, and fourth must be valid indices, and the third must 
be an ellipsis ("...").  The first and fourth indices define the start and end 
of the pattern (inclusive).  The offset between the first and second indices 
defines the step size.  It must be possible to get from the start to the end in 
steps of the given size.

Note that for wells and blocks, the ellipsis pattern can propagate across both 
rows and columns.  In this case, the second index specifies the step size in 
both dimensions.  Consider the ``A1,C3,...,E5`` example from above: C3 is two 
rows and two columns away from A1, so this pattern specifies every odd well 
between A1 and E5.

Precedence rules
================
It is possible to specify multiple values for a single experimental parameter 
in a single well.  The following layout, where `[expt]` and `[well.A1]` both 
specify different samples for the same well, shows a typical way for this to 
happen:

.. code-block:: toml

  [expt]
  sample = 'α'

  [well.A1]
  sample = 'β'

In these situations, which value is used depends on which well group has higher 
"precedence".  Below is a list of each well group, in order from highest to 
lowest precedence.  In general, well groups that are more "specific" have 
higher precedence.  Note that the order in which the wells appear in the layout 
doesn't affect precedence (except for |block| groups having the same area):

- |well|
- |block|

  - If two blocks have different areas, the smaller one has higher precedence.
  - If two blocks have the same area, the one that appears later in the layout 
    has higher precedence.

- |row|
- |col|
- |irow|
- |icol|
- |expt|

|plate| groups do not have their own precedence.  Instead, well groups used 
within |plate| groups have precedence a half-step higher than the same group 
used outside a plate.  In other words, `[plate.NAME.row.A] <[plate.NAME]>` has 
higher precedence than |row|, but lower precedence than |block|.

The following layout is contrived, but visually demonstrates most of the 
precedence rules:

.. example:: file_format/precedence.toml

   [plate.X]

   [plate.Y]
   precedence = 'plate'

   [plate.Z.row.A]
   precedence = 'plate.row'

   [well.A1]
   precedence = 'well'

   [block.2x2.A1]
   precedence = 'block.2x2'

   [block.3x3.A1]
   precedence = 'block.3x3'

   [row.A]
   precedence = 'row'

   [col.1]
   precedence = 'col'

   [expt]
   precedence = 'expt'

   # Specify how many wells to show.
   [block.5x5.A1]


.. _toml: https://github.com/toml-lang/toml
.. _table: https://github.com/toml-lang/toml#table
.. _key_value: https://github.com/toml-lang/toml#keyvalue-pair
.. _key: https://github.com/toml-lang/toml#keys
.. _string: https://github.com/toml-lang/toml#string
.. _integer: https://github.com/toml-lang/toml#integer
.. _float: https://github.com/toml-lang/toml#float
.. _boolean: https://github.com/toml-lang/toml#boolean
.. _date: https://github.com/toml-lang/toml#local-date
.. _time: https://github.com/toml-lang/toml#local-time

