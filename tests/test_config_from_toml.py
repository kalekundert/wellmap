#!/usr/bin/env python3

from bio96 import *
from pathlib import Path
from test_table_from_wells import row

DIR = Path(__file__).parent/'toml'

def test_one_include():
    config, paths, concats = config_from_toml(DIR/'one_include.toml')
    assert config == {
            'well': {
                'A1': {'x': 2, 'y': 1},
            },
    }

def test_two_includes():
    config, paths, concats = config_from_toml(DIR/'two_includes.toml')
    assert config == {
            'well': {
                'A1': {'x': 2, 'y': 1, 'z': 1},
            },
    }

def test_one_concat():
    config, paths, concats = config_from_toml(DIR/'one_concat.toml')
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

    config, paths, concats = config_from_toml(
            DIR/'one_concat.toml',
            path_guess='{0.stem}.xlsx',
    )
    assert config == {
            'well': {
                'A1': {'x': 2},
            }
    }
    assert row(concats[0], 'well == "A1"') == dict(
            path=DIR/'one_well_xy.xlsx',
            well='A1',
            well0='A01',
            row='A', col='1',
            row_i=0, col_j=0,
            x=1,
            y=1,
    )

def test_two_concats():
    config, paths, concats = config_from_toml(
            DIR/'two_concats.toml',
            path_guess='{0.stem}.xlsx',
    )
    assert config == {
            'well': {
                'A1': {'x': 2},
            }
    }
    assert row(concats[0], 'well == "A1"') == dict(
            path=DIR/'one_well_xy.xlsx',
            well='A1',
            well0='A01',
            row='A', col='1',
            row_i=0, col_j=0,
            x=1,
            y=1,
    )
    assert row(concats[1], 'well == "A1"') == dict(
            path=DIR/'one_well_xyz.xlsx',
            well='A1',
            well0='A01',
            row='A', col='1',
            row_i=0, col_j=0,
            x=0,
            y=0,
            z=1,
    )

def test_alert(capsys):
    config, paths, concats = config_from_toml(DIR/'alert.toml')
    assert "Hello world!" in capsys.readouterr().out

    alert = ""
    def on_alert(toml_path, message):
        nonlocal alert
        alert = toml_path, message

    config, paths, concats = config_from_toml(
            DIR/'alert.toml',
            on_alert=on_alert,
    )
    assert alert == (DIR/'alert.toml', "Hello world!")



