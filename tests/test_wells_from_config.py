#!/usr/bin/env python3

from bio96 import *
from pytest import raises

def test_one_well():
    config = {
            'well': {
                'A1': {'x': 1},
            },
    }
    assert wells_from_config(config) == {
            'A1': {'x': 1},
    }

def test_multiple_wells():
    config = {
            'well': {
                'A1': {'x': 1},
                'B2': {'x': 2},
            },
    }
    assert wells_from_config(config) == {
            'A1': {'x': 1},
            'B2': {'x': 2},
    }

def test_one_block():
    config_err = {
            'block': {
                'err': {}
            },
    }
    with raises(ConfigError, match="err"):
        wells_from_config(config_err)

    config_0x0 = {
            'block': {
                '0x0': {
                    'A1': {'x': 1},
                },
            },
    }
    with raises(ConfigError, match="0x0"):
        wells_from_config(config_0x0)

    config_0x1 = {
            'block': {
                '0x1': {
                    'A1': {'x': 1},
                },
            },
    }
    with raises(ConfigError, match="0x1"):
        wells_from_config(config_0x1)

    config_1x0 = {
            'block': {
                '1x0': {
                    'A1': {'x': 1},
                },
            },
    }
    with raises(ConfigError, match="1x0"):
        wells_from_config(config_1x0)

    config_1x1 = {
            'block': {
                '1x1': {
                    'A1': {'x': 1},
                },
            },
    }
    assert wells_from_config(config_1x1) == {
            'A1': {'x': 1},
    }

    config_1x2 = {
            'block': {
                '1x2': {
                    'A1': {'x': 1},
                },
            },
    }
    assert wells_from_config(config_1x2) == {
            'A1': {'x': 1},
            'B1': {'x': 1},
    }

    config_2x1 = {
            'block': {
                '2x1': {
                    'A1': {'x': 1},
                },
            },
    }
    assert wells_from_config(config_2x1) == {
            'A1': {'x': 1},
            'A2': {'x': 1},
    }

    config_2x2 = {
            'block': {
                '2x2': {
                    'A1': {'x': 1},
                },
            },
    }
    assert wells_from_config(config_2x2) == {
            'A1': {'x': 1},
            'A2': {'x': 1},
            'B1': {'x': 1},
            'B2': {'x': 1},
    }

def test_multiple_blocks():
    config = {
            'block': {
                '1x1': {
                    'A1': {'x': 1},
                    'B2': {'x': 2},
                },
            },
    }
    assert wells_from_config(config) == {
            'A1': {'x': 1},
            'B2': {'x': 2},
    }

    config = {
            'block': {
                '2x1': {
                    'A1': {'x': 1},
                },
                '1x2': {
                    'A1': {'y': 1},
                },
            },
    }
    assert wells_from_config(config) == {
            'A1': {'x': 1, 'y': 1},
            'A2': {'x': 1        },
            'B1': {        'y': 1},
    }

def test_one_row_col():
    config = {
            'row': {
                'A': {'x': 1},
            },
            'col': {
                '1': {'y': 1},
            },
    }
    assert wells_from_config(config) == {
            'A1': {'x': 1, 'y': 1},
    }

def test_multiple_rows():
    config = {
            'row': {
                'A': {'x': 1},
                'B': {'x': 2},
            },
            'col': {
                '1': {'y': 1},
            },
    }
    assert wells_from_config(config) == {
            'A1': {'x': 1, 'y': 1},
            'B1': {'x': 2, 'y': 1},
    }

def test_multiple_cols():
    config = {
            'row': {
                'A': {'x': 1},
            },
            'col': {
                '1': {'y': 1},
                '2': {'y': 2},
            },
    }
    assert wells_from_config(config) == {
            'A1': {'x': 1, 'y': 1},
            'A2': {'x': 1, 'y': 2},
    }

def test_row_without_col():
    config = {
            'row': {
                'A': {'x': 1},
            },
    }
    with raises(ConfigError, match="row"):
        wells_from_config(config)

def test_col_without_row():
    config = {
            'col': {
                '1': {'y': 1},
            },
    }
    with raises(ConfigError, match="col"):
        wells_from_config(config)

def test_interleaved_row():
    config = {
            'irow': {
                'A': {'x': 1},
            },
            'col': {
                '1': {'y': 1},
                '2': {'y': 2},
            },
    }
    assert wells_from_config(config) == {
            'A1': {'x': 1, 'y': 1},
            'B2': {'x': 1, 'y': 2},
    }

    config = {
            'irow': {
                'B': {'x': 2},
            },
            'col': {
                '1': {'y': 1},
                '2': {'y': 2},
            },
    }
    assert wells_from_config(config) == {
            'B1': {'x': 2, 'y': 1},
            'A2': {'x': 2, 'y': 2},
    }

def test_interleaved_col():
    config = {
            'row': {
                'A': {'x': 1},
                'B': {'x': 2},
            },
            'icol': {
                '1': {'y': 1},
            },
    }
    assert wells_from_config(config) == {
            'A1': {'x': 1, 'y': 1},
            'B2': {'x': 2, 'y': 1},
    }

    config = {
            'row': {
                'A': {'x': 1},
                'B': {'x': 2},
            },
            'icol': {
                '2': {'y': 2},
            },
    }
    assert wells_from_config(config) == {
            'A2': {'x': 1, 'y': 2},
            'B1': {'x': 2, 'y': 2},
    }

def test_irow_without_col():
    config = {
            'irow': {
                'A': {'x': 1},
            },
    }
    with raises(ConfigError, match="irow"):
        wells_from_config(config)

def test_icol_without_row():
    config = {
            'icol': {
                '1': {'y': 1},
            },
    }
    with raises(ConfigError, match="icol"):
        wells_from_config(config)

def test_top_level_params():
    config = {
            'x': 1,
            'well': {'A1': {}},
    }
    assert wells_from_config(config) == {
            'A1': {'x': 1},
    }

def test_precedence():
    config = {
            'well': {
                'A1': {'a': 1},
            },
            'block': {
                '1x1': {
                    'A1': {'a': 2, 'b': 2},
                },
            },
            'row': {
                'A': {'a': 3, 'b': 3, 'c': 3},
            },
            'col': {
                '1': {'a': 4, 'b': 4, 'd': 4},
            },

            'a': 5,
            'b': 5,
            'c': 5,
            'd': 5,
            'e': 5,
    }
    wells = wells_from_config(config)
    assert wells['A1'] == {
            'a': 1,
            'b': 2,
            'c': 3,
            'd': 4,
            'e': 5,
    }

