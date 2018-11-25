#!/usr/bin/env python3

import re
import string

# Indices
# =======
# `well`
#   A string naming a well, e.g. "A1" or "A01".  Note that columns count from 
#   1.  Rows beyond "Z" can be specified useing multiple letters, e.g. "AA".  
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
        raise ConfigError(f"Cannot parse well '{well}'")

    return m.group(1).upper(), str(int(m.group(2)))


def i_from_row(row):
    if not row.isalpha():
        raise ConfigError("Cannot parse row '{row}'")

    i = 0
    D = len(row) - 1
    N = len(string.ascii_uppercase)

    for d, char in enumerate(row):
        n = ord(char.upper()) - ord('A') + 1
        i += n * N**(D - d)

    return i - 1

def j_from_col(col):
    if not col.isdigit():
        raise ConfigError("Cannot parse column '{col}'")

    return int(col) - 1

def ij_from_well(well):
    return ij_from_row_col(*row_col_from_well(well))

def ij_from_row_col(row, col):
    return i_from_row(row), j_from_col(col)


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

def iter_ij_in_block(top_left, width, height):
    top, left = ij_from_well(top_left)
    for dx in range(width):
        for dy in range(height):
            yield top + dy, left + dx

class ConfigError(Exception):

    def __init__(self, message):
        self.message = message
        self.toml_path = None

    def __str__(self):
        if self.toml_path:
            return f"{self.toml_path}: {self.message}"
        else:
            return self.message
