#!/usr/bin/env python3

import pytest

from wellmap import *
from pathlib import Path
from .test_table_from_wells import row

DIR = Path(__file__).parent/'toml'

def test_one_include():
    config, paths, concats, extras = config_from_toml(DIR/'one_include.toml')
    assert config == {
            'well': {
                'A1': {'x': 2, 'y': 1},
            },
    }

def test_two_includes():
    config, paths, concats, extras = config_from_toml(DIR/'two_includes.toml')
    assert config == {
            'well': {
                'A1': {'x': 2, 'y': 1, 'z': 1},
            },
    }

def test_include_err():
    with pytest.raises(ConfigError, match=r"expected 'meta.include' to be string or list, not \{'.*\}"):
        config_from_toml(DIR/'err_include_dict.toml')
    with pytest.raises(FileNotFoundError):
        config_from_toml(DIR/'err_include_nonexistent.toml')

def test_one_concat():
    config, paths, concats, extras = config_from_toml(DIR/'one_concat.toml')
    assert config == {
            'well': {
                'A1': {'x': 2},
            }
    }
    assert row(concats[0], 'well == "A1"') == dict(
            well='A1',
            well0='A01',
            row='A', col='1',
            row_i=0, col_j=0,
            x=1,
            y=1,
    )

    config, paths, concats, extras = config_from_toml(
            DIR/'one_concat.toml',
            path_guess='{0.stem}.csv',
    )
    assert config == {
            'well': {
                'A1': {'x': 2},
            }
    }
    assert row(concats[0], 'well == "A1"') == dict(
            path=DIR/'one_well_xy.csv',
            well='A1',
            well0='A01',
            row='A', col='1',
            row_i=0, col_j=0,
            x=1,
            y=1,
    )

def test_two_concats_list():
    config, paths, concats, extras = config_from_toml(
            DIR/'two_concats_list.toml',
            path_guess='{0.stem}.csv',
    )
    assert config == {
            'well': {
                'A1': {'x': 2},
            }
    }
    assert row(concats[0], 'well == "A1"') == dict(
            path=DIR/'one_well_xy.csv',
            well='A1',
            well0='A01',
            row='A', col='1',
            row_i=0, col_j=0,
            x=1,
            y=1,
    )
    assert row(concats[1], 'well == "A1"') == dict(
            path=DIR/'one_well_xyz.csv',
            well='A1',
            well0='A01',
            row='A', col='1',
            row_i=0, col_j=0,
            x=0,
            y=0,
            z=1,
    )

def test_two_concats_dict():
    config, paths, concats, extras = config_from_toml(
            DIR/'two_concats_dict.toml',
            path_guess='{0.stem}.csv',
    )
    assert config == {
            'well': {
                'A1': {'x': 2},
            }
    }
    assert row(concats[0], 'well == "A1"') == dict(
            path=DIR/'one_well_xy.csv',
            plate='a',
            well='A1',
            well0='A01',
            row='A', col='1',
            row_i=0, col_j=0,
            x=1,
            y=1,
    )
    assert row(concats[1], 'well == "A1"') == dict(
            path=DIR/'one_well_xyz.csv',
            plate='b',
            well='A1',
            well0='A01',
            row='A', col='1',
            row_i=0, col_j=0,
            x=0,
            y=0,
            z=1,
    )

def test_concat_err():
    with pytest.raises(ConfigError, match=r"expected 'meta.concat' to be string, list, or dictionary, not 0"):
        config_from_toml(DIR/'err_concat_wrong_type.toml')
    with pytest.raises(FileNotFoundError):
        config_from_toml(DIR/'err_concat_nonexistent.toml')

def test_one_extra():
    config, paths, concats, extras = config_from_toml(
            DIR/'extras.toml',
            extras='a',
    )
    assert extras == {
            'a': {'b': 1},
    }

def test_two_extras():
    config, paths, concats, extras = config_from_toml(
            DIR/'extras.toml',
            extras=['a.b', 'c'],
    )
    assert extras == {
            'a.b': 1,
            'c': 2,
    }

def test_alert(capsys):
    config, paths, concats, extras = config_from_toml(DIR/'alert.toml')
    assert "Hello world!" in capsys.readouterr().out

    alert = ""
    def on_alert(toml_path, message):
        nonlocal alert
        alert = toml_path, message

    config, paths, concats, extras = config_from_toml(
            DIR/'alert.toml',
            on_alert=on_alert,
    )
    assert alert == (DIR/'alert.toml', "Hello world!")



