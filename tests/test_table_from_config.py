#!/usr/bin/env python3

from bio96 import *
from test_table_from_wells import row

class DummyPathManager:

    def check_named_plates(self, names):
        pass

    def get_index_for_only_plate(self):
        return {'path': '/path/to/data'}

    def get_index_for_named_plate(self, name):
        return {'plate': name, 'path': f'/path/to/{name.lower()}'}

def test_only_plate():
    config = {
            'well': {
                'A1': {'x': 1},
            },
    }
    df = table_from_config(config, DummyPathManager())
    assert row(df, 'well == "A1"') == dict(
            path='/path/to/data',
            well='A1',
            row='A', col='1',
            row_i=0, col_j=0,
            x=1,
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
                        'A1': {'x': 1},
                    },
                },
            },
    }
    df = table_from_config(config, DummyPathManager())

    assert row(df, 'plate == "Q"') == dict(
            plate='Q',
            path='/path/to/q',
            well='A1',
            row='A', col='1',
            row_i=0, col_j=0,
            x=1,
    )
    assert row(df, 'plate == "R"') == dict(
            plate='R',
            path='/path/to/r',
            well='A1',
            row='A', col='1',
            row_i=0, col_j=0,
            x=1,
    )

def test_named_plates_with_defaults():
    config = {
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
            row='A', col='1',
            row_i=0, col_j=0,
            x=2,
            y=1,
    )
    assert row(df, 'plate == "R"') == dict(
            plate='R',
            path='/path/to/r',
            well='A1',
            row='A', col='1',
            row_i=0, col_j=0,
            x=1,
            y=2,
    )
