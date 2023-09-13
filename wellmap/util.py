#!/usr/bin/env python3

import re
import string
import functools
import contextlib

from difflib import get_close_matches
from copy import deepcopy

def require_well_locations(df):
    """
    Make sure that the given data frame has `plate`, `row_i`, and `col_j` columns.
    """
    rows_i = cols_j = None

    def still_missing_locs():
        return rows_i is None or cols_j is None

    if 'row_i' in df:
        rows_i = df['row_i']
    elif 'row' in df:
        rows_i = df['row'].map(i_from_row)

    if 'col_j' in df:
        cols_j = df['col_j']
    elif 'col' in df:
        cols_j = df['col'].map(j_from_col)

    for well in ['well', 'well0']:
        if well in df and still_missing_locs():
            ij = df.apply(
                    lambda x: ij_from_well(x[well]),
                    axis=1,
                    result_type='expand',
            )
            rows_i = ij[0]
            cols_j = ij[1]

    if still_missing_locs():
        raise LayoutError(f"Can't find well locations.\nData frame must have 1-2 of the following columns: 'well', 'well0', 'row', 'col', 'row_i', 'col_j'\nColumns found: {quoted_join(df.columns)}")

    df = df.copy()

    if 'plate' not in df:
        df['plate'] = ''

    # The int cast is most important for data frames that originated in R, 
    # where everything is a float by default.
    df['row_i'] = rows_i.astype(int)
    df['col_j'] = cols_j.astype(int)

    # This is just so that the data frame is nicer to look at during debugging.
    loc_cols = ['plate', 'well', 'well0', 'row', 'col', 'row_i', 'col_j']
    loc_ranks = {k: i for i, k in enumerate(loc_cols)}

    def by_location(col):
        rank = loc_ranks.get(col, len(loc_cols))
        return rank

    df = df[sorted(df.columns, key=by_location)]

    return df


def well_from_row_col(row, col):
    """
    Create a well name from the given row and column names.

    Example::

        >>> well_from_row_col('A', '2')
        'A2'

    See also: :doc:`/well_formats`
    """
    return f'{row}{int(col)}'

def well_from_ij(i, j):
    """
    Create a well name from the given row and column indices.

    Example::

        >>> well_from_ij(0, 1)
        'A2'

    See also: :doc:`/well_formats`
    """
    return well_from_row_col(
            row_from_i(i),
            col_from_j(j),
    )

def well0_from_well(well, digits=2):
    """
    Create a zero-padded well name from the given well name.

    It doesn't matter if the input name is zero-padded or not.

    Example::

        >>> well0_from_well('A2')
        'A02'

    See also: :doc:`/well_formats`
    """
    row, col = row_col_from_well(well)
    return well0_from_row_col(row, col, digits)

def well0_from_row_col(row, col, digits=2):
    """
    Create a zero-padded well name from the given row and column names.

    Example::

        >>> well0_from_row_col('A', '2')
        'A02'

    See also: :doc:`/well_formats`
    """
    return f'{row}{int(col):0{digits}}'


def row_from_i(i):
    """
    Convert the given index into a row name.

    The row after 'Z' is 'AA'.

    Example::

        >>> row_from_i(0)
        'A'

    See also: :doc:`/well_formats`
    """
    if i < 0:
        raise LayoutError("Cannot reference negative rows")

    row = ''
    N = len(string.ascii_uppercase)

    while i >= 0:
        row = string.ascii_uppercase[i % N] + row
        i  = (i // N) - 1

    return row

def col_from_j(j):
    """
    Convert the given index into a column name.

    Note that column names count from 1, and are strings.

    Example::

        >>> col_from_j(0)
        '1'

    See also: :doc:`/well_formats`
    """
    if j < 0:
        raise LayoutError("Cannot reference negative columns")

    return str(j + 1)

def row_col_from_ij(i, j):
    """
    Convert the given indices into row and column names.

    Example::

        >>> row_col_from_ij(0, 1)
        'A', '2'

    See also: :doc:`/well_formats`
    """
    return row_from_i(i), col_from_j(j)

def row_col_from_well(well):
    """
    Split row and column names out of the given well name.

    The well name is allowed to be zero-padded.

    Example::

        >>> row_col_from_well('A2')
        'A', '2'

    See also: :doc:`/well_formats`
    """
    m = re.match('([A-Za-z]+)([0-9]+)', well)
    if not m:
        raise LayoutError(f"Cannot parse well '{well}', expected 'A1', 'B2', etc.")

    return m.group(1).upper(), str(int(m.group(2)))


def i_from_row(row):
    """
    Convert the given row name into an index number.

    Example::

        >>> i_from_row('A')
        0

    See also: :doc:`/well_formats`
    """
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
    """
    Convert the given column name into an index number.

    Note that column names count from 1.  It doesn't matter if the name 
    is zero-padded or not.

    Example::

        >>> j_from_col('1')
        0
        >>> j_from_col('01')
        0

    See also: :doc:`/well_formats`
    """
    if not col.isdigit():
        raise LayoutError(f"Cannot parse column '{col}', expected digit(s) e.g. '1', '2', etc.")

    return int(col) - 1

def ij_from_well(well):
    """
    Convert the given well name into row and column indices.

    It doesn't matter if the column number is zero-padded or not.

    Example::

        >>> ij_from_well('A2')
        (0, 1)
        >>> ij_from_well('A02')
        (0, 1)

    See also: :doc:`/well_formats`
    """
    return ij_from_row_col(*row_col_from_well(well))

def ij_from_row_col(row, col):
    """
    Convert the given row and column names into indices.

    It doesn't matter if the column number is zero-padded or not.

    Example::

        >>> ij_from_row_col('A', '2')
        (0, 1)
        >>> ij_from_row_col('A', '02')
        (0, 1)

    See also: :doc:`/well_formats`
    """
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

def iter_ij_in_block(top_left_ij, width, height):
    """
    Yield all of the well indices in the given block.

    Example::

        >>> list(iter_ij_in_block((0,1), 2, 2))
        [(0, 1), (0, 2), (1, 1), (1, 2)]

    See also: :doc:`/well_formats`
    """
    i, j = top_left_ij
    for di in range(height):
        for dj in range(width):
            yield i + di, j + dj

def iter_indices(pattern, index_from_solo, indices_from_range):
    tokens = pattern.split(',')

    @contextlib.contextmanager
    def format_layout_err(**kwargs):
        try:
            yield
        except LayoutError as err:
            err.message = f"{pattern!r}: {err.message.format_map(kwargs)}"
            raise err

    if '...' in tokens:
        if len(tokens) != 4 or tokens.index('...') != 2:
            raise LayoutError(f"Expected '<first>,<second>,...,<last>', not '{pattern}'")

        x0 = index_from_solo(tokens[0])
        x1 = index_from_solo(tokens[1])
        xn = index_from_solo(tokens[3])

        # Delegate this to another function, because it has to be done 
        # differently for wells than for rows/cols.
        with format_layout_err(
                first=tokens[0],
                second=tokens[1],
                last=tokens[3],
        ):
            yield from indices_from_range(x0, x1, xn)

    else:
        for token in tokens:
            if '-' not in token:
                yield index_from_solo(token)

            else:
                endpoints = token.split('-')

                if len(endpoints) != 2:
                    raise LayoutError(f"Expected '<first>-<last>', not '{token}'")

                x0 = index_from_solo(endpoints[0])
                xn = index_from_solo(endpoints[1])

                with format_layout_err(
                        first=endpoints[0],
                        last=endpoints[1],
                ):
                    yield from indices_from_range(x0, xn)

def iter_row_indices(pattern):
    """
    Yield all of the well indices in the given row(s).

    The given pattern can either specify a single row (e.g. "A") or several, 
    using the pattern syntax (e.g. "A,B", "A-C", "A,C,...,G").

    Examples::

        >>> list(iter_row_indices('A'))
        [0]
        >>> list(wellmap.iter_row_indices('A,B'))
        [0, 1]
        >>> list(wellmap.iter_row_indices('A-C'))
        [0, 1, 2]

    See also: :doc:`/well_formats`
    """
    yield from iter_indices(pattern, i_from_row, indices_from_range)

def iter_col_indices(pattern):
    """
    Yield all of the well indices in the given column(s).

    The given pattern can either specify a single column (e.g. "1") or several, 
    using the pattern syntax (e.g. "1,2", "1-3", "1,3,...,11").

    Examples::

        >>> list(iter_col_indices('1'))
        [0]
        >>> list(wellmap.iter_col_indices('1,2'))
        [0, 1]
        >>> list(wellmap.iter_col_indices('1-3'))
        [0, 1, 2]

    See also: :doc:`/well_formats`
    """
    yield from iter_indices(pattern, j_from_col, indices_from_range)

def iter_well_indices(pattern):
    """
    Yield the indices for the given well(s).

    The given pattern can either specify a single well (e.g. "A1") or several, 
    using the pattern syntax (e.g. "A1,B2", "A1-B2", "A1,A3,...,B11").

    Examples::

        >>> list(wellmap.iter_well_indices('A1'))
        [(0, 0)]
        >>> list(wellmap.iter_well_indices('A1,B2'))
        [(0, 0), (1, 1)]
        >>> list(wellmap.iter_well_indices('A1-B2'))
        [(0, 0), (0, 1), (1, 0), (1, 1)]

    See also: :doc:`/well_formats`
    """

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

    yield from iter_indices(pattern, ij_from_well, ijs_from_range)


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
    The `shift_pattern` function does.
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

def shift_pattern(pattern, shift):
    """
    Shift the given row/column/well/pattern by the given amount.

    This function is very similar to `shift_row_col`, except that it also 
    handles patterns (e.g. 'A1,A2,...,A12').
    """

    def shift_row_col_ellipsis(token, shift):
        if token == '...':
            return token
        else:
            return shift_row_col(token, shift)

    return ','.join(
            shift_row_col_ellipsis(x, shift)
            for x in pattern.split(',')
    )

def add_shifts(a, b):
    (a1, a2), (b1, b2) = a, b
    return a1 + b1, a2 + b2

def sub_shifts(a, b):
    (a1, a2), (b1, b2) = a, b
    return a1 - b1, a2 - b2

def map_keys(dict, func, *, level=0):
    """
    Transform the keys of the given dictionary with the given function.

    If a level is specified, the values of the dictionary are expected to be 
    dictionaries themselves (up to the given level), and only the keys at the 
    specified level will be transformed.

    This is used in the context of shifting wells from an included layout.  
    """
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


def recursive_merge(config, defaults, overwrite=False):
    for key, default in defaults.items():
        if isinstance(default, dict):
            if isinstance(config.get(key, {}), dict):
                config.setdefault(key, {})
                recursive_merge(config[key], default, overwrite)
            elif overwrite:
                config[key] = deepcopy(default)
        else:
            if overwrite or key not in config:
                config[key] = default

    # Modified in-place, but also returned for convenience.
    return config


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

class StyleAttributeError(AttributeError):

    def __init__(self, unknown_attr, known_attrs, is_param_level=False):
        self.unknown_attr = unknown_attr
        self.known_attrs = known_attrs
        self.is_param_level = is_param_level

    def __str__(self):
        return self.format()

    def format(self, toml_syntax=False):
        if toml_syntax:
            if self.is_param_level:
                attr_type = '[meta.param_styles]'
            else:
                attr_type = '[meta.style]'
        else:
            if self.is_param_level:
                attr_type = 'param-level style'
            else:
                attr_type = 'style'

        message = f"{self.unknown_attr!r} is not a valid {attr_type} attribute"

        close_matches = get_close_matches(
                self.unknown_attr,
                self.known_attrs,
                n=1,
        )
        if close_matches:
            message += f"\nDid you mean: {close_matches[0]!r}"

        return message

    def as_layout_error(self):
        return LayoutError(self.format(toml_syntax=True))

