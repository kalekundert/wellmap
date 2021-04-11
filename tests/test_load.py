#!/usr/bin/env python3

import pytest
import wellmap
import pandas as pd
from pathlib import Path
from pytest import raises
from wellmap import ConfigError
from .test_table_from_wells import row

DIR = Path(__file__).parent/'toml'

def read_csv_and_rename(path):
    return pd.read_csv(path).rename({'Well': 'well'})


def test_one_well():
    labels = wellmap.load(DIR/'one_well_xy.toml')
    assert row(labels, 'well == "A1"') == dict(
            well='A1',
            well0='A01',
            row='A', col='1',
            row_i=0, col_j=0,
            x=1,
            y=1,
    )

    labels = wellmap.load(DIR/'one_well_xy.toml', path_guess='{0.stem}.csv')
    assert row(labels, 'well == "A1"') == dict(
            path=DIR/'one_well_xy.csv',
            well='A1',
            well0='A01',
            row='A', col='1',
            row_i=0, col_j=0,
            x=1,
            y=1,
    )

    _, deps = wellmap.load(DIR/'one_well_xy.toml', report_dependencies=True)
    assert deps == {
            DIR/'one_well_xy.toml'
    }

    with raises(ConfigError, match='one_well_xy.toml'):
        wellmap.load(DIR/'one_well_xy.toml', path_required=True)
    with raises(ConfigError, match='one_well_xy.toml'):
        wellmap.load(DIR/'one_well_xy.toml', data_loader=pd.read_csv)

    labels, data = wellmap.load(
            DIR/'one_well_xy.toml',
            data_loader=pd.read_csv,
            path_guess='{0.stem}.csv',
    )
    assert row(labels, 'well == "A1"') == dict(
            path=DIR/'one_well_xy.csv',
            well='A1',
            well0='A01',
            row='A', col='1',
            row_i=0, col_j=0,
            x=1,
            y=1,
    )
    assert row(data, 'Well == "A1"') == dict(
            Well='A1',
            path=DIR/'one_well_xy.csv',
            Data='xy',
    )

    df = wellmap.load(
            DIR/'one_well_xy.toml',
            data_loader=pd.read_csv,
            merge_cols={'well': 'Well'},
            path_guess='{0.stem}.csv',
    )
    assert row(df, 'well == "A1"') == dict(
            path=DIR/'one_well_xy.csv',
            well='A1',
            Well='A1',
            well0='A01',
            row='A', col='1',
            row_i=0, col_j=0,
            x=1,
            y=1,
            Data='xy',
    )

    df = wellmap.load(
            DIR/'one_well_xy.toml',
            data_loader=read_csv_and_rename,
            merge_cols=True,
            path_guess='{0.stem}.csv',
    )
    assert row(df, 'well == "A1"') == dict(
            path=DIR/'one_well_xy.csv',
            well='A1',
            Well='A1',
            well0='A01',
            row='A', col='1',
            row_i=0, col_j=0,
            x=1,
            y=1,
            Data='xy',
    )

def test_one_well_with_extras():
    expected = {'extras': {'a': 1, 'b': 1}}

    def data_loader(path, extras):
        assert extras == expected
        return pd.read_csv(path)

    # No data:
    a1_expected = dict(
            well='A1',
            well0='A01',
            row='A', col='1',
            row_i=0, col_j=0,
            x=1,
            y=1,
    )

    labels, extras = wellmap.load(
            DIR/'one_well_xy_extras.toml',
            extras=True,
    )
    assert row(labels, 'well == "A1"') == a1_expected
    assert extras == expected

    # No data, with extras present but not requested:
    labels = wellmap.load(
            DIR/'one_well_xy_extras.toml',
    )
    assert row(labels, 'well == "A1"') == a1_expected

    # No data, with extras and dependencies requested:
    labels, extras, deps = wellmap.load(
            DIR/'one_well_xy_extras.toml',
            extras=True,
            report_dependencies=True,
    )
    assert row(labels, 'well == "A1"') == a1_expected
    assert extras == expected
    assert deps == {
            DIR/'one_well_xy_extras.toml',
    }

    # Load labels and data, but don't merge:
    labels, data, extras = wellmap.load(
            DIR/'one_well_xy_extras.toml',
            data_loader=data_loader,
            path_guess='{0.stem}.csv',
            extras=True,
    )
    assert row(labels, 'well == "A1"') == dict(
            path=DIR/'one_well_xy_extras.csv',
            well='A1',
            well0='A01',
            row='A', col='1',
            row_i=0, col_j=0,
            x=1,
            y=1,
    )
    assert row(data, 'Well == "A1"') == dict(
            Well='A1',
            path=DIR/'one_well_xy_extras.csv',
            Data='xy',
    )
    assert extras == expected

    # Automatic merge:
    a1_expected = dict(
            path=DIR/'one_well_xy_extras.csv',
            well='A1',
            Well='A1',
            well0='A01',
            row='A', col='1',
            row_i=0, col_j=0,
            x=1,
            y=1,
            Data='xy',
    )

    df, extras = wellmap.load(
            DIR/'one_well_xy_extras.toml',
            data_loader=data_loader,
            merge_cols={'well': 'Well'},
            path_guess='{0.stem}.csv',
            extras=True,
    )
    assert row(df, 'well == "A1"') == a1_expected
    assert extras == expected

    df, extras = wellmap.load(
            DIR/'one_well_xy_extras.toml',
            data_loader=read_csv_and_rename,
            merge_cols=True,
            path_guess='{0.stem}.csv',
            extras=True,
    )
    assert row(df, 'well == "A1"') == a1_expected
    assert extras == expected

def test_one_plate():
    labels = wellmap.load(DIR/'one_plate.toml')
    assert row(labels, 'well == "A1"') == dict(
            path=DIR/'one_plate.csv',
            plate='a',
            well='A1',
            well0='A01',
            row='A', col='1',
            row_i=0, col_j=0,
            x=1,
    )

def test_two_plates():
    df = wellmap.load(
            DIR/'two_plates.toml',
            data_loader=pd.read_csv,
            merge_cols={'well': 'Well'},
    )
    assert row(df, 'plate == "a"') == dict(
            path=DIR/'two_plates_a.csv',
            plate='a',
            well='A1',
            Well='A1',
            well0='A01',
            row='A', col='1',
            row_i=0, col_j=0,
            x=1,
            Data=0,
    )
    assert row(df, 'plate == "b"') == dict(
            path=DIR/'two_plates_b.csv',
            plate='b',
            well='A1',
            Well='A1',
            well0='A01',
            row='A', col='1',
            row_i=0, col_j=0,
            x=2,
            Data=1,

    )

def test_concat():
    labels = wellmap.load(DIR/'one_concat.toml')
    assert len(labels) == 2

    with raises(ConfigError, match="Did you mean to set `meta.path`?"):
        wellmap.load(DIR/'one_concat.toml', path_required=True)

    labels = wellmap.load(DIR/'two_concats_list.toml')
    assert len(labels) == 3

    with raises(ConfigError, match="Did you mean to set `meta.path`?"):
        wellmap.load(DIR/'two_concats_list.toml', path_required=True)

    # Should not raise.  It's ok that `just_concat.csv` doesn't exist, because
    # `just_concat.toml` doesn't specify any wells.
    labels = wellmap.load(
            DIR/'just_concat.toml',
            path_guess='{0.stem}.csv',
            path_required=True,
    )
    assert len(labels) == 1

def test_reasonably_complex():
    df = wellmap.load(DIR/'reasonably_complex.toml')
    assert len(df) == 32

def test_no_wells():
    with raises(ConfigError, match="No wells defined"):
        wellmap.load(DIR/"empty.toml")

    # The following examples actually trigger a different (and more specific) 
    # exception, but it still has "No wells defined" in the message.
    with raises(ConfigError, match="No wells defined"):
        wellmap.load(DIR/"row_without_col.toml")
    with raises(ConfigError, match="No wells defined"):
        wellmap.load(DIR/"irow_without_col.toml")
    with raises(ConfigError, match="No wells defined"):
        wellmap.load(DIR/"col_without_row.toml")
    with raises(ConfigError, match="No wells defined"):
        wellmap.load(DIR/"icol_without_row.toml")

def test_bad_args():

    # Doesn't make sense to specify `merge_cols` without `data_loader`:
    with raises(ValueError):
        wellmap.load(DIR/'two_plates.toml', merge_cols={})

    # Non-existent merge columns.
    with raises(ValueError, match='xxx'):
        wellmap.load(
                DIR/'two_plates.toml',
                data_loader=pd.read_csv,
                merge_cols={'xxx': 'Well'},
        )

    with raises(ValueError, match='xxx'):
        wellmap.load(
                DIR/'two_plates.toml',
                data_loader=pd.read_csv,
                merge_cols={'well': 'xxx'},
        )


