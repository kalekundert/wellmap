#!/usr/bin/env python3

import pytest

from wellmap import *
from pathlib import Path
from .test_table_from_wells import row

DIR = Path(__file__).parent/'toml'

def test_one_include():
    config, paths, concats, extras, deps = config_from_toml(
            DIR/'one_include.toml',
    )
    assert config == {
            'well': {
                'A1': {'x': 2, 'y': 1},
            },
    }
    assert concats == []
    assert extras == {}
    assert deps == {
            DIR/'one_include.toml',
            DIR/'one_well_xy.toml',
    }

def test_two_includes():
    config, paths, concats, extras, deps = config_from_toml(
            DIR/'two_includes.toml',
    )
    assert config == {
            'well': {
                'A1': {'x': 2, 'y': 1, 'z': 1},
            },
    }
    assert concats == []
    assert extras == {}
    assert deps == {
            DIR/'two_includes.toml',
            DIR/'one_well_xy.toml',
            DIR/'one_well_xyz.toml',
    }

def test_nested_includes():
    config, paths, concats, extras, deps = config_from_toml(
            DIR/'nested_includes.toml',
    )
    assert config == {
            'well': {
                'A1': {'x': 2, 'y': 1, 'z': 3},
            },
    }
    assert concats == []
    assert extras == {}
    assert deps == {
            DIR/'nested_includes.toml',
            DIR/'one_include.toml',
            DIR/'one_well_xy.toml',
    }

def test_include_concat():
    config, paths, concats, extras, deps = config_from_toml(
            DIR/'include_concat.toml',
    )
    assert config == {
            'well': {
                'A2': {'x': 3, 'y': 2},
            },
    }
    assert row(concats[0], 'well == "A1"') == dict(
            well='A1',
            well0='A01',
            row='A', col='1',
            row_i=0, col_j=0,
            x=1,
            y=1,
    )
    assert extras == {}
    assert deps == {
            DIR/'include_concat.toml',
            DIR/'one_concat.toml',
            DIR/'one_well_xy.toml',
    }

def test_include_err():
    with pytest.raises(ConfigError, match=r"expected 'meta.include' to be string or list, not \{'.*\}"):
        config_from_toml(DIR/'err_include_dict.toml')
    with pytest.raises(FileNotFoundError):
        config_from_toml(DIR/'err_include_nonexistent.toml')

def test_one_concat():
    config, paths, concats, extras, deps = config_from_toml(
            DIR/'one_concat.toml',
    )
    assert config == {
            'well': {
                'A2': {'x': 2, 'y': 2},
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
    assert extras == {}
    assert deps == {
            DIR/'one_concat.toml',
            DIR/'one_well_xy.toml',
    }

    config, paths, concats, extras, deps = config_from_toml(
            DIR/'one_concat.toml',
            path_guess='{0.stem}.csv',
    )
    assert config == {
            'well': {
                'A2': {'x': 2, 'y': 2},
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
    assert extras == {}
    assert deps == {
            DIR/'one_concat.toml',
            DIR/'one_well_xy.toml',
    }

def test_two_concats_list():
    config, paths, concats, extras, deps = config_from_toml(
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
    assert extras == {}
    assert deps == {
            DIR/'two_concats_list.toml',
            DIR/'one_well_xy.toml',
            DIR/'one_well_xyz.toml',
    }

def test_two_concats_dict():
    config, paths, concats, extras, deps = config_from_toml(
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
    assert extras == {}
    assert deps == {
            DIR/'two_concats_dict.toml',
            DIR/'one_well_xy.toml',
            DIR/'one_well_xyz.toml',
    }

def test_nested_concats():
    config, paths, concats, extras, deps = config_from_toml(
            DIR/'nested_concats.toml',
    )
    assert config == {
            'well': {
                'A3': {'x': 3, 'y': 3},
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
    assert row(concats[0], 'well == "A2"') == dict(
            well='A2',
            well0='A02',
            row='A', col='2',
            row_i=0, col_j=1,
            x=2,
            y=2,
    )
    assert extras == {}
    assert deps == {
            DIR/'nested_concats.toml',
            DIR/'one_concat.toml',
            DIR/'one_well_xy.toml',
    }

def test_concat_err():
    with pytest.raises(ConfigError, match=r"expected 'meta.concat' to be string, list, or dictionary, not 0"):
        config_from_toml(DIR/'err_concat_wrong_type.toml')
    with pytest.raises(FileNotFoundError):
        config_from_toml(DIR/'err_concat_nonexistent.toml')

@pytest.mark.parametrize(
        'params', [
            dict(
                path=DIR/'just_extras_ab.toml',
                expected={'extras': {'a': 1, 'b': 1}},
            ),
            dict(
                path=DIR/'include_extras.toml',
                expected={'extras': {'a': 1, 'b': 1}},
            ),
            dict(
                path=DIR/'include_two_extras.toml',
                expected={'extras': {'a': 2, 'b': 1, 'c': 1}},
            ),

            # Concatenated files are not searched for extras.
            dict(
                path=DIR/'concat_extras.toml',
                expected={},
            ),
        ]
)
def test_extras(params):
    config, paths, concats, extras, deps = config_from_toml(
            params['path'],
    )
    assert extras == params['expected']

@pytest.mark.parametrize(
        'path, expected_alerts', [(
            DIR/'just_alert.toml', [
                (DIR/'just_alert.toml', "Hello world!"),
            ],
        ), (
            DIR/'include_alert.toml', [
                (DIR/'just_alert.toml', "Hello world!"),
                (DIR/'include_alert.toml', "Goodbye world!"),
            ],
        ), (
            DIR/'concat_alert.toml', [
                (DIR/'one_well_xy_alert.toml', "Hello world!"),
                (DIR/'concat_alert.toml', "Goodbye world!"),
            ],
)])
def test_alert(path, expected_alerts, capsys):
    # Test the default alert handler (print to stderr).
    config, paths, concats, extras, deps = config_from_toml(path)
    stderr = capsys.readouterr().err

    for expected_path, expected_alert in expected_alerts:
        assert expected_path.name in stderr
        assert expected_alert in stderr

    # Test a custom alert handler.
    actual_alerts = []
    def on_alert(toml_path, message):
        actual_alerts.append((toml_path, message))

    config, paths, concats, extras, deps = config_from_toml(
            path,
            on_alert=on_alert,
    )
    assert actual_alerts == expected_alerts

