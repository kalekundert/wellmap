#!/usr/bin/env python3

import pytest
from hypothesis import given
from hypothesis.strategies import integers
from bio96 import *

def test_well_from_row_col():
    assert well_from_row_col('A', 1) == 'A1'
    assert well_from_row_col('A', '1') == 'A1'
    assert well_from_row_col('A', '01') == 'A1'

def test_well_from_irow_col():
    assert well_from_irow_col('A', '1') == 'A1'
    assert well_from_irow_col('A', '2') == 'B2'
    assert well_from_irow_col('B', '1') == 'B1'
    assert well_from_irow_col('B', '2') == 'A2'

def test_well_from_row_icol():
    assert well_from_row_icol('A', '1') == 'A1'
    assert well_from_row_icol('B', '1') == 'B2'
    assert well_from_row_icol('A', '2') == 'A2'
    assert well_from_row_icol('B', '2') == 'B1'

def test_well_from_ij():
    assert well_from_ij(0, 0) == 'A1'
    assert well_from_ij(0, 1) == 'A2'
    assert well_from_ij(1, 0) == 'B1'
    assert well_from_ij(1, 1) == 'B2'


def test_i_from_row():
    assert i_from_row('A') == 0
    assert i_from_row('B') == 1

def test_j_from_col():
    assert j_from_col('1') == 0
    assert j_from_col('2') == 1

    assert j_from_col('01') == 0
    assert j_from_col('02') == 1

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


def test_row_from_i():
    assert row_from_i(0) == 'A'
    assert row_from_i(1) == 'B'

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

def test_irow_icol_from_well():
    assert irow_icol_from_well('A1') == ('A', '1')
    assert irow_icol_from_well('A2') == ('B', '2')
    assert irow_icol_from_well('B1') == ('B', '2')
    assert irow_icol_from_well('B2') == ('A', '1')

    assert irow_icol_from_well('A01') == ('A', '1')
    assert irow_icol_from_well('A02') == ('B', '2')
    assert irow_icol_from_well('B01') == ('B', '2')
    assert irow_icol_from_well('B02') == ('A', '1')


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



