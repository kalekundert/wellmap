#!/usr/bin/env python3

import pytest
from pytest import raises
from hypothesis import given
from hypothesis.strategies import integers
from bio96 import *

# A,B,...,A   I think this might pass my checks, but it shouldn't be allowed.

def test_well_from_row_col():
    assert well_from_row_col('A', 1) == 'A1'
    assert well_from_row_col('A', '1') == 'A1'
    assert well_from_row_col('A', '01') == 'A1'

def test_well_from_ij():
    assert well_from_ij(0, 0) == 'A1'
    assert well_from_ij(0, 1) == 'A2'
    assert well_from_ij(1, 0) == 'B1'
    assert well_from_ij(1, 1) == 'B2'

def test_well0_from_well():
    assert well0_from_well('A1', 1) == 'A1'
    assert well0_from_well('A1', 2) == 'A01'
    assert well0_from_well('A1', 3) == 'A001'

    assert well0_from_well('A01', 1) == 'A1'
    assert well0_from_well('A01', 2) == 'A01'
    assert well0_from_well('A01', 3) == 'A001'

def test_well0_from_row_col():
    assert well0_from_row_col('A', '1', 1) == 'A1'
    assert well0_from_row_col('A', '1', 2) == 'A01'
    assert well0_from_row_col('A', '1', 3) == 'A001'

    assert well0_from_row_col('A', '01', 1) == 'A1'
    assert well0_from_row_col('A', '01', 2) == 'A01'
    assert well0_from_row_col('A', '01', 3) == 'A001'

def test_row_from_i():
    assert row_from_i(0) == 'A'
    assert row_from_i(1) == 'B'

    assert row_from_i(25) == 'Z'
    assert row_from_i(26) == 'AA'
    assert row_from_i(27) == 'AB'

    assert row_from_i(51) == 'AZ'
    assert row_from_i(52) == 'BA'
    assert row_from_i(53) == 'BB'

def test_col_from_j():
    assert col_from_j(0) == '1'
    assert col_from_j(1) == '2'

def test_row_col_from_ij():
    assert row_col_from_ij(0, 0) == ('A', '1')
    assert row_col_from_ij(0, 1) == ('A', '2')
    assert row_col_from_ij(1, 0) == ('B', '1')
    assert row_col_from_ij(1, 1) == ('B', '2')

def test_row_col_from_well():
    assert row_col_from_well('A1') == ('A', '1')
    assert row_col_from_well('A2') == ('A', '2')
    assert row_col_from_well('B1') == ('B', '1')
    assert row_col_from_well('B2') == ('B', '2')

    assert row_col_from_well('A01') == ('A', '1')
    assert row_col_from_well('A02') == ('A', '2')
    assert row_col_from_well('B01') == ('B', '1')
    assert row_col_from_well('B02') == ('B', '2')

    assert row_col_from_well('AA1') == ('AA', '1')
    assert row_col_from_well('AA2') == ('AA', '2')
    assert row_col_from_well('BB1') == ('BB', '1')
    assert row_col_from_well('BB2') == ('BB', '2')

    assert row_col_from_well('AA01') == ('AA', '1')
    assert row_col_from_well('AA02') == ('AA', '2')
    assert row_col_from_well('BB01') == ('BB', '1')
    assert row_col_from_well('BB02') == ('BB', '2')

    with raises(ConfigError, match="XXX"):
        row_col_from_well('XXX')
    with raises(ConfigError, match="123"):
        row_col_from_well('123')
    with raises(ConfigError, match="1A"):
        row_col_from_well('1A')


def test_i_from_row():
    examples = {
            'A':   0,
            'B':   1,
            'Z':  25,
            'AA': 26,
            'AB': 27,
            'AZ': 51,
            'BA': 52,
            'BB': 53,
    }
    for row, i in examples.items():
        assert i_from_row(row.upper()) == i
        assert i_from_row(row.lower()) == i

    with raises(ConfigError):
        i_from_row('')
    with raises(ConfigError):
        i_from_row('1')
    with raises(ConfigError):
        i_from_row('A1')

def test_j_from_col():
    assert j_from_col('1') == 0
    assert j_from_col('2') == 1

    assert j_from_col('01') == 0
    assert j_from_col('02') == 1

    with raises(ConfigError):
        j_from_col('')
    with raises(ConfigError):
        j_from_col('A')
    with raises(ConfigError):
        j_from_col('A1')

def test_ij_from_well():
    assert ij_from_well('A1') == (0, 0)
    assert ij_from_well('A2') == (0, 1)
    assert ij_from_well('B1') == (1, 0)
    assert ij_from_well('B2') == (1, 1)

    assert ij_from_well('A01') == (0, 0)
    assert ij_from_well('A02') == (0, 1)
    assert ij_from_well('B01') == (1, 0)
    assert ij_from_well('B02') == (1, 1)

def test_ij_from_row_col():
    assert ij_from_row_col('A', '1') == (0, 0)
    assert ij_from_row_col('A', '2') == (0, 1)
    assert ij_from_row_col('B', '1') == (1, 0)
    assert ij_from_row_col('B', '2') == (1, 1)

    assert ij_from_row_col('A', '01') == (0, 0)
    assert ij_from_row_col('A', '02') == (0, 1)
    assert ij_from_row_col('B', '01') == (1, 0)
    assert ij_from_row_col('B', '02') == (1, 1)


def test_interleave():
    examples = [
            (0, 0, 0), (1, 0, 1), (2, 0, 2), (3, 0, 3),
            (0, 1, 1), (1, 1, 0), (2, 1, 3), (3, 1, 2),
            (0, 2, 0), (1, 2, 1), (2, 2, 2), (3, 2, 3),
            (0, 3, 1), (1, 3, 0), (2, 3, 3), (3, 3, 2),
    ]
    for a, b, x in examples:
        assert interleave(a, b) == x

@given(integers(), integers())
def test_interleave_is_its_own_inverse(a, b):
    assert interleave(interleave(a, b), b) == a


def test_check_range():
    # Should pass the check (not raise):
    check_range(0, 1, 2)
    check_range(0, 1, 3)

    check_range(0, 2, 4)
    check_range(0, 2, 6)

    check_range(0, 1, 1, True)

    # Should fail the check (out of order):
    with raises(ConfigError):
        check_range(0, 0, 0)
    with raises(ConfigError):
        check_range(0, 0, 1)
    with raises(ConfigError):
        check_range(0, 1, 1)
    with raises(ConfigError):
        check_range(1, 1, 1)
    with raises(ConfigError):
        check_range(0, 2, 1)

    # Should fail the check (don't add up):
    with raises(ConfigError, match="in steps of 2"):
        check_range(0, 2, 3)
    with raises(ConfigError, match="in steps of 2"):
        check_range(0, 2, 5)
    with raises(ConfigError, match="in steps of 3"):
        check_range(0, 3, 5)

def test_inclusive_range():
    inc_range = lambda *args: list(inclusive_range(*args))

    assert inc_range(0, 1, 1) == [0, 1]
    assert inc_range(0, 1, 2) == [0, 1, 2]
    assert inc_range(0, 2, 2) == [0, 2]
    assert inc_range(0, 2, 4) == [0, 2, 4]

def test_iter_row_indices():
    # A B C D E F G H
    # 0 1 2 3 4 5 6 7

    legal = {
            'A': [0],
            'B': [1],

            'A,B': [0, 1],
            'B,C': [1, 2],

            'A,B,...,C': [0,1,2],
            'A,B,...,D': [0,1,2,3],
            'A,C,...,E': [0,2,4],
            'A,C,...,G': [0,2,4,6],

            'B,C,...,D': [1,2,3],
            'B,C,...,E': [1,2,3,4],
            'B,D,...,F': [1,3,5],
            'B,D,...,H': [1,3,5,7],
    }
    for key, value in legal.items():
        assert list(iter_row_indices(key)) == value

    illegal = {
        '1': "Cannot parse row '1'",
        'A,...,B,D': "Expected '<first>,<second>,...,<last>', not 'A,...,B,D'",
        'A,B,...,B': "'A,B,...,B': Expected A < B < B",
        'A,C,...,D': "'A,C,...,D': Cannot get from A to D in steps of 2",
    }
    for key, err in illegal.items():
        with raises(ConfigError, match=err):
            list(iter_row_indices(key))

def test_iter_col_indices():
    legal = {
            '1': [0],
            '2': [1],

            '1,2': [0, 1],
            '2,3': [1, 2],

            '1,2,...,3': [0,1,2],
            '1,2,...,4': [0,1,2,3],
            '1,3,...,5': [0,2,4],
            '1,3,...,7': [0,2,4,6],

            '2,3,...,4': [1,2,3],
            '2,3,...,5': [1,2,3,4],
            '2,4,...,6': [1,3,5],
            '2,4,...,8': [1,3,5,7],
    }
    for key, value in legal.items():
        assert list(iter_col_indices(key)) == value

    illegal = {
        'A': "Cannot parse column 'A'",
        '1,...,2,4': "Expected '<first>,<second>,...,<last>', not '1,...,2,4'",
        '1,2,...,2': "'1,2,...,2': Expected 1 < 2 < 2",
        '1,3,...,4': "'1,3,...,4': Cannot get from 1 to 4 in steps of 2",
    }
    for key, err in illegal.items():
        with raises(ConfigError, match=err):
            list(iter_col_indices(key))

def test_iter_well_indices():
    legal = {
            'A1': {(0,0)},
            'B2': {(1,1)},

            'A1,A2': {(0,0), (0,1)},
            'B2,B3': {(1,1), (1,2)},

            # Single row
            'A1,A2,...,A3': {(0,0),(0,1),(0,2)},
            'A1,A2,...,A4': {(0,0),(0,1),(0,2),(0,3)},
            'A1,A3,...,A5': {(0,0),(0,2),(0,4)},
            'A1,A3,...,A7': {(0,0),(0,2),(0,4),(0,6)},

            'B2,B3,...,B4': {(1,1),(1,2),(1,3)},
            'B2,B3,...,B5': {(1,1),(1,2),(1,3),(1,4)},
            'B2,B4,...,B6': {(1,1),(1,3),(1,5)},
            'B2,B4,...,B8': {(1,1),(1,3),(1,5),(1,7)},

            # Single column
            'A1,B1,...,C1': {(0,0),(1,0),(2,0)},
            'A1,B1,...,D1': {(0,0),(1,0),(2,0),(3,0)},
            'A1,C1,...,E1': {(0,0),(2,0),(4,0)},
            'A1,C1,...,G1': {(0,0),(2,0),(4,0),(6,0)},

            'B2,C2,...,D2': {(1,1),(2,1),(3,1)},
            'B2,C2,...,E2': {(1,1),(2,1),(3,1),(4,1)},
            'B2,D2,...,F2': {(1,1),(3,1),(5,1)},
            'B2,D2,...,H2': {(1,1),(3,1),(5,1),(7,1)},

            # Rows and columns
            'A1,B2,...,B2': {(0,0),(0,1),(1,0),(1,1)},
            'B2,C3,...,C3': {(1,1),(1,2),(2,1),(2,2)},
            'A1,C3,...,C5': {(0,0),(0,2),(0,4),(2,0),(2,2),(2,4)},
            'A1,C3,...,E3': {(0,0),(0,2),(2,0),(2,2),(4,0),(4,2)},
    }
    for key, value in legal.items():
        assert set(iter_well_indices(key)) == value

    illegal = {
        'A': "Cannot parse well 'A'",
        '1': "Cannot parse well '1'",
        'A1,...,B2,D4': "Expected '<first>,<second>,...,<last>', not 'A1,...,B2,D4'",
        'A1,B1,...,B1': "'A1,B1,...,B1': Expected A1 < B1 < B1",
        'A1,A2,...,A2': "'A1,A2,...,A2': Expected A1 < A2 < A2",
        'A1,C3,...,D5': "'A1,C3,...,D5': Cannot get from A1 to D5 in steps of 2",
        'A1,C3,...,E4': "'A1,C3,...,E4': Cannot get from A1 to E4 in steps of 2",
    }
    for key, err in illegal.items():
        with raises(ConfigError, match=err):
            list(iter_well_indices(key))
        


