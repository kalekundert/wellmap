#!/usr/bin/env python3

import string

def well_from_row_col(row, col):
    return f'{row}{int(col)}'

def well_from_irow_col(irow, col):
    ii, j = ij_from_row_col(irow, col)
    i = interleave(ii, j)
    return well_from_ij(i, j)

def well_from_row_icol(row, icol):
    i, jj = ij_from_row_col(row, icol)
    j = interleave(jj, i)
    return well_from_ij(i, j)

def well_from_ij(i, j):
    return well_from_row_col(
            row_from_i(i),
            col_from_j(j),
    )


def i_from_row(row):
    return ord(row.upper()) - ord('A')

def j_from_col(col):
    return int(col) - 1

def ij_from_well(well):
    return ij_from_row_col(*row_col_from_well(well))

def ij_from_row_col(row, col):
    return i_from_row(row), j_from_col(col)


def row_from_i(i):
    return string.ascii_uppercase[i]

def col_from_j(j):
    return str(j + 1)

def row_col_from_ij(i, j):
    return row_from_i(i), col_from_j(j)

def row_col_from_well(well):
    return well[:1], str(int(well[1:]))

def irow_icol_from_well(well):
    row, col = row_col_from_well(well)
    i, j = ij_from_row_col(row, col)
    ii = interleave(i, j)
    jj = interleave(j, i)
    return row_col_from_ij(ii, jj)


def interleave(a, b):
    """
    Convert the given coordinates between "real" and "interleaved" space.

    Only the first coordinate differs between the two spaces.  A straight row 
    in "interleaved" space will alternative between two adjacent rows in "real" 
    space, and vice versa.  This function can also used to interleave 
    columns (by passing the column as the first argument and the row as the 
    second).

    Note that this function is its own inverse.
    """
    if a % 2 == 0:
        return a + b % 2
    else:
        return a - b % 2

def iter_wells_in_block(top_left, width, height):
    top, left = ij_from_well(top_left)
    for dx in range(width):
        for dy in range(height):
            yield well_from_ij(top + dy, left + dx)

