#!/usr/bin/env python3

import bio96
from pathlib import Path
from test_table_from_wells import row

DIR = Path(__file__).parent/'toml'

def test_one_well():
    df = bio96.load(DIR/'one_well.toml')
    assert row(df, 'well == "A1"') == dict(
            well='A1',
            row='A', col='1',
            row_i=0, col_j=0,
            x=1,
    )

    df = bio96.load(DIR/'one_well.toml', '{0.stem}.dat')
    assert row(df, 'well == "A1"') == dict(
            path=DIR/'one_well.dat',
            well='A1',
            row='A', col='1',
            row_i=0, col_j=0,
            x=1,
    )

def test_one_plate():
    df = bio96.load(DIR/'one_plate.toml')
    assert row(df, 'well == "A1"') == dict(
            path=DIR/'one_plate.dat',
            plate='a',
            well='A1',
            row='A', col='1',
            row_i=0, col_j=0,
            x=1,
    )

def test_two_plates():
    df = bio96.load(DIR/'two_plates.toml')
    assert row(df, 'plate == "a"') == dict(
            path=DIR/'two_plates_a.dat',
            plate='a',
            well='A1',
            row='A', col='1',
            row_i=0, col_j=0,
            x=1,
    )
    assert row(df, 'plate == "b"') == dict(
            path=DIR/'two_plates_b.dat',
            plate='b',
            well='A1',
            row='A', col='1',
            row_i=0, col_j=0,
            x=2,
    )

def test_reasonably_complex():
    df = bio96.load(DIR/'reasonably_complex.toml')
    print(df)
    assert len(df) == 32

