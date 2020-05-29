#!/usr/bin/env python3

from wellmap import *
from pytest import raises
from .test_table_from_wells import row

class DummyPathManager:

    def check_named_plates(self, names):
        pass

    def get_index_for_only_plate(self):
        return {'path': '/path/to/data'}

    def get_index_for_named_plate(self, name):
        return {'plate': name, 'path': f'/path/to/{name.lower()}'}

def test_only_plate():
    config = {
            'expt': {
                'y': 2,
            },
            'well': {
                'A1': {'x': 1},
            },
    }
    df = table_from_config(config, DummyPathManager())
    assert row(df, 'well == "A1"') == dict(
            path='/path/to/data',
            well='A1',
            well0='A01',
            row='A', col='1',
            row_i=0, col_j=0,
            x=1,
            y=2,
    )

def test_named_plates():
    config = {
            'plate': {
                'Q': {
                    'well': {
                        'A1': {'x': 1},
                    },
                },
                'R': {
                    'well': {
                        'A1': {'x': 2},
                    },
                },
            },
    }
    df = table_from_config(config, DummyPathManager())

    assert row(df, 'plate == "Q"') == dict(
            plate='Q',
            path='/path/to/q',
            well='A1',
            well0='A01',
            row='A', col='1',
            row_i=0, col_j=0,
            x=1,
    )
    assert row(df, 'plate == "R"') == dict(
            plate='R',
            path='/path/to/r',
            well='A1',
            well0='A01',
            row='A', col='1',
            row_i=0, col_j=0,
            x=2,
    )

def test_named_plates_with_defaults():
    config = {
            'expt': {
                'z': 1,
            },
            'well': {
                'A1': {'x': 1, 'y': 1},
            },
            'plate': {
                'Q': {
                    'well': {
                        'A1': {'x': 2},
                    },
                },
                'R': {
                    'well': {
                        'A1': {'y': 2},
                    },
                },
            },
    }
    df = table_from_config(config, DummyPathManager())

    assert row(df, 'plate == "Q"') == dict(
            plate='Q',
            path='/path/to/q',
            well='A1',
            well0='A01',
            row='A', col='1',
            row_i=0, col_j=0,
            x=2,
            y=1,
            z=1,
    )
    assert row(df, 'plate == "R"') == dict(
            plate='R',
            path='/path/to/r',
            well='A1',
            well0='A01',
            row='A', col='1',
            row_i=0, col_j=0,
            x=1,
            y=2,
            z=1,
    )

def test_top_level():
    config = {
            'plate': {
                'Q': {
                    'y': 3,
                    'well': {
                        'A1': {'x': 1},
                    },
                },
                'R': {
                    'y': 4,
                    'well': {
                        'A1': {'x': 2},
                    },
                },
            },
    }
    df = table_from_config(config, DummyPathManager())

    assert row(df, 'plate == "Q"') == dict(
            plate='Q',
            path='/path/to/q',
            well='A1',
            well0='A01',
            row='A', col='1',
            row_i=0, col_j=0,
            x=1,
            y=3,
    )
    assert row(df, 'plate == "R"') == dict(
            plate='R',
            path='/path/to/r',
            well='A1',
            well0='A01',
            row='A', col='1',
            row_i=0, col_j=0,
            x=2,
            y=4,
    )

def test_no_plate_name():
    config = {
            'plate': {
                'x': 1,
            },
    }
    with raises(ConfigError, match="Illegal attribute 'x'"):
        table_from_config(config, DummyPathManager())

def test_expt_in_plate():
    config = {
            'plate': {
                'Q': {
                    'expt': 1,
                },
            },
    }
    with raises(ConfigError, match=r"\[expt\] in \[plate\]"):
        table_from_config(config, DummyPathManager())
