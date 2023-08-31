************
Well formats
************

The wellmap APIs accommodate a number of different ways to specify the location 
of a well.  The following terminology is used (as consistently as possible) to 
distinguish between these formats, and to be clear about which is being used in 
any context:

*well*:
  A string naming a well, e.g. "A1".  Note that columns count from 1.  Rows 
  beyond "Z" can be specified using multiple letters, e.g. "AA".

*well0*:
  The same as *well*, but with the column numbers padded to two digits with 
  leading zeros, e.g. "A01".

*row*, *col*:
  The individual row (letter) or column (number) parts of a well.  Note that 
  these column numbers count from 1.

*row_i*, *col_j*:
  The numeric coordinates of a well, counting from 0.  For example, "A1" is 
  (0,0), "A2" is (0, 1), "B1" is (1, 0), etc.  Sometimes these indices are 
  just referred to as *i* and *j*, if the fact that we're talking about rows 
  and columns is clear from the context.

*pattern*:
  A string like that may specify multiple wells/rows/columns, like "A1,A2" or 
  "A-D".  In other words, a string that may use the pattern syntax.  It's also 
  possible for a pattern string to specify only a single well/row/column.
