#!/usr/bin/env python3

import bio96
import pandas as pd
from pathlib import Path
from pytest import raises
from bio96 import ConfigError
from test_table_from_wells import row

DIR = Path(__file__).parent/'toml'

def test_one_well():
    labels = bio96.load(DIR/'one_well_xy.toml')
    assert row(labels, 'well == "A1"') == dict(
            well='A1',
            row='A', col='1',
            row_i=0, col_j=0,
            x=1,
            y=1,
    )

    labels = bio96.load(DIR/'one_well_xy.toml', path_guess='{0.stem}.xlsx')
    assert row(labels, 'well == "A1"') == dict(
            path=DIR/'one_well_xy.xlsx',
            well='A1',
            row='A', col='1',
            row_i=0, col_j=0,
            x=1,
            y=1,
    )

    with raises(ConfigError, match='one_well_xy.toml'):
        bio96.load(DIR/'one_well_xy.toml', path_required=True)
    with raises(ConfigError, match='one_well_xy.toml'):
        bio96.load(DIR/'one_well_xy.toml', data_loader=pd.read_excel)

    labels, data = bio96.load(
            DIR/'one_well_xy.toml',
            data_loader=pd.read_excel,
            path_guess='{0.stem}.xlsx',
    )
    assert row(labels, 'well == "A1"') == dict(
            path=DIR/'one_well_xy.xlsx',
            well='A1',
            row='A', col='1',
            row_i=0, col_j=0,
            x=1,
            y=1,
    )
    assert row(data, 'Well == "A1"') == dict(
            Well='A1',
            path=DIR/'one_well_xy.xlsx',
            Data='xy',
    )

    df = bio96.load(
            DIR/'one_well_xy.toml',
            data_loader=pd.read_excel,
            merge_cols={'well': 'Well'},
            path_guess='{0.stem}.xlsx',
    )
    assert row(df, 'well == "A1"') == dict(
            path=DIR/'one_well_xy.xlsx',
            well='A1',
            Well='A1',
            row='A', col='1',
            row_i=0, col_j=0,
            x=1,
            y=1,
            Data='xy',
    )

def test_one_plate():
    labels = bio96.load(DIR/'one_plate.toml')
    assert row(labels, 'well == "A1"') == dict(
            path=DIR/'one_plate.xlsx',
            plate='a',
            well='A1',
            row='A', col='1',
            row_i=0, col_j=0,
            x=1,
    )

def test_two_plates():
    df = bio96.load(
            DIR/'two_plates.toml',
            data_loader=pd.read_excel,
            merge_cols={'well': 'Well'},
    )
    assert row(df, 'plate == "a"') == dict(
            path=DIR/'two_plates_a.xlsx',
            plate='a',
            well='A1',
            Well='A1',
            row='A', col='1',
            row_i=0, col_j=0,
            x=1,
            Data=0,
    )
    assert row(df, 'plate == "b"') == dict(
            path=DIR/'two_plates_b.xlsx',
            plate='b',
            well='A1',
            Well='A1',
            row='A', col='1',
            row_i=0, col_j=0,
            x=2,
            Data=1,

    )

def test_concat():
    labels = bio96.load(DIR/'one_concat.toml')
    print(labels)
    assert len(labels) == 2

    labels = bio96.load(DIR/'two_concats.toml')
    print(labels)
    assert len(labels) == 3

def test_reasonably_complex():
    df = bio96.load(DIR/'reasonably_complex.toml')
    assert len(df) == 32

def test_bad_args():

    # Doesn't make sense to specify `merge_cols` without `data_loader`:
    with raises(ValueError):
        bio96.load(DIR/'two_plates.toml', merge_cols={})

    # Non-existent merge columns.
    with raises(ValueError):
        bio96.load(
                DIR/'two_plates.toml',
                data_loader=pd.read_excel,
                merge_cols={'xxx': 'Well'},
        )

    with raises(ValueError):
        bio96.load(
                DIR/'two_plates.toml',
                data_loader=pd.read_excel,
                merge_cols={'well': 'xxx'},
        )
