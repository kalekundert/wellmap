#!/usr/bin/env python3

import pytest
from pytest import raises
from hypothesis import given
from hypothesis.strategies import integers
from bio96 import *

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



