#!/usr/bin/env python3

from wellmap import *
nan = float("NaN")

def row(df, q):
    return df.query(q).iloc[0].dropna().to_dict()


def test_one_well():
    wells = {
            (0,0): {'x': 1},
    }
    df = table_from_wells(wells, {})
    assert row(df, 'well == "A1"') == dict(
            well='A1',
            well0='A01',
            row='A',
            col='1',
            row_i=0,
            col_j=0,
            x=1
    )

def test_different_parameters():
    # We should get NaN `y` in A1 (0,0) and `x` in B1 (1,0)
    wells = {
            (0,0): {'x': 1},
            (1,0): {'y': 2},
    }
    df = table_from_wells(wells, {})
    assert row(df, 'well == "A1"') == dict(
            well='A1',
            well0='A01',
            row='A',
            col='1',
            row_i=0,
            col_j=0,
            x=1,
    )
    assert row(df, 'well == "B1"') == dict(
            well='B1',
            well0='B01',
            row='B',
            col='1',
            row_i=1,
            col_j=0,
            y=2,
    )

def test_index():
    wells = {
            (0,0): {'x': 1},
            (1,0): {'x': 2},
    }
    df = table_from_wells(wells, {'plate': 'Z'})
    assert row(df, 'well == "A1"') == dict(
            plate='Z',
            well='A1',
            well0='A01',
            row='A',
            col='1',
            row_i=0,
            col_j=0,
            x=1,
    )
    assert row(df, 'well == "B1"') == dict(
            plate='Z',
            well='B1',
            well0='B01',
            row='B',
            col='1',
            row_i=1,
            col_j=0,
            x=2,
    )

