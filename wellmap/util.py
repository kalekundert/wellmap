#!/usr/bin/env python3

import re
import string

# Indices
# =======
# `well`
#   A string naming a well, e.g. "A1" or "A01".  Note that columns count from 
#   1.  Rows beyond "Z" can be specified using multiple letters, e.g. "AA".  
#
# `well0`
#   The same as `well`, but with the column numbers padded with leading zeros.
#
# `row`, `col`
#   The individual row (letter) or column (number) parts of a well.
#
# `i`, `j`
#   The (row, column) numeric coordinates of a well, counting from 0.  For 
#   example, "A1" is (0,0), "A2" is (0, 1), "B1" is (1, 0), etc.

def well_from_row_col(row, col):
    return f'{row}{int(col)}'

def well_from_ij(i, j):
    return well_from_row_col(
            row_from_i(i),
            col_from_j(j),
    )

def well0_from_well(well, digits=2):
    row, col = row_col_from_well(well)
    return well0_from_row_col(row, col, digits)

def well0_from_row_col(row, col, digits=2):
    return f'{row}{int(col):0{digits}}'


def row_from_i(i):
    row = ''
    N = len(string.ascii_uppercase)

    while i >= 0:
        row = string.ascii_uppercase[i % N] + row
        i  = (i // N) - 1

    return row

def col_from_j(j):
    return str(j + 1)

def row_col_from_ij(i, j):
    return row_from_i(i), col_from_j(j)

def row_col_from_well(well):
    m = re.match('([A-Za-z]+)([0-9]+)', well)
    if not m:
        raise ConfigError(f"Cannot parse well '{well}', expected 'A1', 'B2', etc.")

    return m.group(1).upper(), str(int(m.group(2)))


def i_from_row(row):
    if not row.isalpha():
        raise ConfigError(f"Cannot parse row '{row}', expected letter(s) e.g. 'A', 'B', etc.")

    i = 0
    D = len(row) - 1
    N = len(string.ascii_uppercase)

    for d, char in enumerate(row):
        n = ord(char.upper()) - ord('A') + 1
        i += n * N**(D - d)

    return i - 1

def j_from_col(col):
    if not col.isdigit():
        raise ConfigError(f"Cannot parse column '{col}', expected digit(s) e.g. '1', '2', etc.")

    return int(col) - 1

def ij_from_well(well):
    return ij_from_row_col(*row_col_from_well(well))

def ij_from_row_col(row, col):
    return i_from_row(row), j_from_col(col)


def interleave(a, b):
    """
    Convert the given coordinates between "real" and "interleaved" space.

    Only the first coordinate differs between the two spaces.  A straight row 
    in "interleaved" space will alternate between two adjacent rows in "real" 
    space, and vice versa.  This function can also used to interleave 
    columns (by passing the column as the first argument and the row as the 
    second).

    Note that this function is its own inverse.
    """
    if a % 2 == 0:
        return a + b % 2
    else:
        return a - b % 2

def iter_ij_in_block(top_left, width, height):
    i, j = top_left
    for di in range(height):
        for dj in range(width):
            yield i + di, j + dj


def iter_indices(key, index_from_subkey, indices_from_range):
    subkeys = key.split(',')

    if '...' not in subkeys:
        yield from map(index_from_subkey, subkeys)

    else:
        if len(subkeys) != 4 or subkeys.index('...') != 2:
            raise ConfigError(f"Expected '<first>,<second>,...,<last>', not '{key}'")

        x0 = index_from_subkey(subkeys[0])
        x1 = index_from_subkey(subkeys[1])
        xn = index_from_subkey(subkeys[3])

        try:
            # Delegate this to another function, because it has to be done 
            # differently for wells than for rows/cols.
            yield from indices_from_range(x0, x1, xn)

        except ConfigError as err:
            err.message = f"'{key}': {err.message.format(*subkeys)}"
            raise err

def iter_row_indices(key):
    yield from iter_indices(key, i_from_row, indices_from_range)

def iter_col_indices(key):
    yield from iter_indices(key, j_from_col, indices_from_range)

def iter_well_indices(key):

    def ijs_from_range(x0, x1, xn):
        i0, j0 = x0
        i1, j1 = x1
        iz, jz = xn

        # Handle the cases where all the indices are in the same row or column 
        # specially, because these cases would otherwise trigger edge 
        # conditions in check_range() and inclusive_range() that I don't want 
        # to allow generally.

        if i0 == i1 == iz:
            yield from ((i0, j) for j in indices_from_range(j0, j1, jz))

        elif j0 == j1 == jz:
            yield from ((i, j0) for i in indices_from_range(i0, i1, iz))

        else:
            check_range(i0, i1, iz, True)
            check_range(j0, j1, jz, True)
            yield from (
                    (i, j)
                    for i in inclusive_range(i0, i1, iz)
                    for j in inclusive_range(j0, j1, jz)
            )

    yield from iter_indices(key, ij_from_well, ijs_from_range)

def check_range(x0, x1, xn, single_step_ok=False):
    """
    Raise a `ConfigError` if you can't get from the first element to the last 
    in steps of the given size.
    """
    # row/col indices are filled into the error messages by `iter_indices()`.
    if not x0 < x1 < (xn + single_step_ok):
        raise ConfigError(f"Expected {{0}} < {{1}} {'≤' if single_step_ok else '<'} {{3}}.")
    if (xn - x0) % (x1 - x0) != 0:
        raise ConfigError(f"Cannot get from {{0}} to {{3}} in steps of {x1-x0}.")

def inclusive_range(x0, x1, xn):
    return range(x0, xn+1, x1-x0)  # xn+1 because range is exclusive.

def indices_from_range(x0, x1, xn):
    check_range(x0, x1, xn)
    yield from inclusive_range(x0, x1, xn)


def get_dotted_key(dict, key):
    result = dict
    subkeys = []

    for subkey in key.split('.'):
        subkeys.append(subkey)

        try:
            result = result[subkey.strip()]
        except KeyError:
            raise KeyError('.'.join(subkeys)) from None

    return result

def quoted_join(it):
    return ', '.join(f"'{x}'" for x in it)

class ConfigError(Exception):

    def __init__(self, message):
        self.message = message
        self.toml_path = None

    def __str__(self):
        if self.toml_path:
            return f"{self.toml_path}: {self.message}"
        else:
            return self.message
