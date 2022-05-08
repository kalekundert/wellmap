#!/usr/bin/env python3

import re
import string
import functools
import contextlib

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
    if i < 0:
        raise LayoutError("Cannot reference negative rows")

    row = ''
    N = len(string.ascii_uppercase)

    while i >= 0:
        row = string.ascii_uppercase[i % N] + row
        i  = (i // N) - 1

    return row

def col_from_j(j):
    if j < 0:
        raise LayoutError("Cannot reference negative columns")

    return str(j + 1)

def row_col_from_ij(i, j):
    return row_from_i(i), col_from_j(j)

def row_col_from_well(well):
    m = re.match('([A-Za-z]+)([0-9]+)', well)
    if not m:
        raise LayoutError(f"Cannot parse well '{well}', expected 'A1', 'B2', etc.")

    return m.group(1).upper(), str(int(m.group(2)))


def i_from_row(row):
    if not row.isalpha():
        raise LayoutError(f"Cannot parse row '{row}', expected letter(s) e.g. 'A', 'B', etc.")

    i = 0
    D = len(row) - 1
    N = len(string.ascii_uppercase)

    for d, char in enumerate(row):
        n = ord(char.upper()) - ord('A') + 1
        i += n * N**(D - d)

    return i - 1

def j_from_col(col):
    if not col.isdigit():
        raise LayoutError(f"Cannot parse column '{col}', expected digit(s) e.g. '1', '2', etc.")

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

    @contextlib.contextmanager
    def format_layout_err(**kwargs):
        try:
            yield
        except LayoutError as err:
            err.message = f"'{key}': {err.message.format_map(kwargs)}"
            raise err

    if '...' in subkeys:
        if len(subkeys) != 4 or subkeys.index('...') != 2:
            raise LayoutError(f"Expected '<first>,<second>,...,<last>', not '{key}'")

        x0 = index_from_subkey(subkeys[0])
        x1 = index_from_subkey(subkeys[1])
        xn = index_from_subkey(subkeys[3])

        # Delegate this to another function, because it has to be done 
        # differently for wells than for rows/cols.
        with format_layout_err(
                first=subkeys[0],
                second=subkeys[1],
                last=subkeys[3],
        ):
            yield from indices_from_range(x0, x1, xn)

    else:
        for subkey in subkeys:
            if '-' not in subkey:
                yield index_from_subkey(subkey)

            else:
                endpoints = subkey.split('-')

                if len(endpoints) != 2:
                    raise LayoutError(f"Expected '<first>-<last>', not '{subkey}'")

                x0 = index_from_subkey(endpoints[0])
                xn = index_from_subkey(endpoints[1])

                with format_layout_err(
                        first=endpoints[0],
                        last=endpoints[1],
                ):
                    yield from indices_from_range(x0, xn)

def iter_row_indices(key):
    yield from iter_indices(key, i_from_row, indices_from_range)

def iter_col_indices(key):
    yield from iter_indices(key, j_from_col, indices_from_range)

def iter_well_indices(key):

    @x1_optional
    def ijs_from_range(x0, x1, xn):
        i0, j0 = x0
        i1, j1 = x1 if x1 is not None else (None, None)
        iz, jz = xn

        # Handle the cases where all the indices are in the same row or column 
        # specially, because these cases would otherwise trigger edge 
        # conditions in check_range() and inclusive_range() that I don't want 
        # to allow generally.

        if (i0 == iz) and (i1 == i0 or i1 is None):
            yield from ((i0, j) for j in indices_from_range(j0, j1, jz))

        elif (j0 == jz) and (j1 == j0 or j1 is None):
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
    Raise a `LayoutError` if you can't get from the first element to the last 
    in steps of the given size.
    """
    # row/col indices are filled into the error messages by `iter_indices()`.
    if x1 is None:
        if not x0 < (xn + single_step_ok):
            raise LayoutError(f"Expected {{first}} {'≤' if single_step_ok else '<'} {{last}}")
    else:
        if not x0 < x1 < (xn + single_step_ok):
            raise LayoutError(f"Expected {{first}} < {{second}} {'≤' if single_step_ok else '<'} {{last}}.")
        if (xn - x0) % (x1 - x0) != 0:
            raise LayoutError(f"Cannot get from {{first}} to {{last}} in steps of {x1-x0}.")

def x1_optional(f):

    @functools.wraps(f)
    def wrapper(*args):
        if len(args) == 2:
            x0, xn = args
            args = x0, None, xn

        return f(*args)

    return wrapper

@x1_optional
def inclusive_range(x0, x1, xn):
    dx = x1 - x0 if x1 is not None else 1
    return range(x0, xn+1, dx)  # xn+1 because range is exclusive.

@x1_optional
def indices_from_range(x0, x1, xn):
    check_range(x0, x1, xn)
    yield from inclusive_range(x0, x1, xn)

def range_from_indices(*xs):
    return range(min(xs), max(xs) + 1) if xs else []


def parse_shift(shift_str):
    """
    Return the (Δrow, Δcolumn) tuple corresponding to the given human-readable 
    string (e.g. "A1 to B2").
    """
    src_dest = shift_str.split(' to ')
    if len(src_dest) != 2:
        raise LayoutError(f"expected 'meta.include.shift' to match the form '<well> to <well>', got: {shift_str}")

    ij_src = ij_from_well(src_dest[0])
    ij_dest = ij_from_well(src_dest[1])

    return sub_shifts(ij_dest, ij_src)

def shift_row_col(row_col, shift):
    """
    Shift the given row/column/well name by the given amount.

    Note that this function does not handle patterns, e.g. 'A1,A2,...,A12'.  
    The `shift_key` function does.
    """
    m = re.fullmatch('([A-Za-z]+)?([0-9]+)?', row_col)

    if not m or not row_col:
        raise LayoutError(f"Cannot parse '{row_col}' as a row, column, or well name.")

    row, col = m.groups()
    di, dj = shift

    if row and col:
        i, j = ij_from_row_col(row, col)
        return well_from_ij(i + di, j + dj)

    if row and not col:
        i = i_from_row(row)
        return row_from_i(i + di)

    if col and not row:
        j= j_from_col(col)
        return col_from_j(j + dj)

    assert False

def shift_key(key, shift):
    """
    Shift the given row/column/well/pattern by the given amount.

    This function is very similar to `shift_row_col`, except that it also 
    handles patterns.
    """

    def shift_row_col_ellipsis(k, shift):
        if k == '...':
            return k
        else:
            return shift_row_col(k, shift)

    return ','.join(
            shift_row_col_ellipsis(k, shift)
            for k in key.split(',')
    )

def add_shifts(a, b):
    (a1, a2), (b1, b2) = a, b
    return a1 + b1, a2 + b2

def sub_shifts(a, b):
    (a1, a2), (b1, b2) = a, b
    return a1 - b1, a2 - b2

def map_keys(dict, func, *, level=0):
    if level:
        return {
                k: map_keys(v, func, level=level-1)
                for k, v in dict.items()
        }
    else:
        return {
                func(k): v
                for k, v in dict.items()
        }


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

class LayoutError(Exception):

    def __init__(self, message):
        self.message = message
        self.toml_path = None

    def __str__(self):
        if self.toml_path:
            return f"{self.toml_path}: {self.message}"
        else:
            return self.message
