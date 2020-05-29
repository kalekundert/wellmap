#!/usr/bin/env python3

from wellmap import *
from pytest import raises

def test_one_well():
    config = {
            'well': {
                'XXX': {'x': 1},
            },
    }
    with raises(ConfigError, match='XXX'):
        wells_from_config(config)

    config = {
            'well': {
                'A1': {'x': 1},
            },
    }
    assert wells_from_config(config) == {
            (0,0): {'x': 1},
    }

def test_multiple_wells():
    config = {
            'well': {
                'A1': {'x': 1},
                'B2': {'x': 2},
            },
    }
    assert wells_from_config(config) == {
            (0,0): {'x': 1},
            (1,1): {'x': 2},
    }

def test_well_range():
    config = {
            'well': {
                'A1,A2': {'x': 1},
            },
    }
    assert wells_from_config(config) == {
            (0,0): {'x': 1},
            (0,1): {'x': 1},
    }

    config = {
            'well': {
                'A1,A3,...,A5': {'x': 1},
            },
    }
    assert wells_from_config(config) == {
            (0,0): {'x': 1},
            (0,2): {'x': 1},
            (0,4): {'x': 1},
    }

    config = {
            'well': {
                'A1,C1,...,E1': {'x': 1},
            },
    }
    assert wells_from_config(config) == {
            (0,0): {'x': 1},
            (2,0): {'x': 1},
            (4,0): {'x': 1},
    }

    config = {
            'well': {
                'A1,C3,...,E7': {'x': 1},
            },
    }
    assert wells_from_config(config) == {
            (0,0): {'x': 1},
            (0,2): {'x': 1},
            (0,4): {'x': 1},
            (0,6): {'x': 1},
            (2,0): {'x': 1},
            (2,2): {'x': 1},
            (2,4): {'x': 1},
            (2,6): {'x': 1},
            (4,0): {'x': 1},
            (4,2): {'x': 1},
            (4,4): {'x': 1},
            (4,6): {'x': 1},
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
            (0,0): {'x': 1},
    }

    config_1x2 = {
            'block': {
                '1x2': {
                    'A1': {'x': 1},
                },
            },
    }
    assert wells_from_config(config_1x2) == {
            (0,0): {'x': 1},
            (1,0): {'x': 1},
    }

    config_2x1 = {
            'block': {
                '2x1': {
                    'A1': {'x': 1},
                },
            },
    }
    assert wells_from_config(config_2x1) == {
            (0,0): {'x': 1},
            (0,1): {'x': 1},
    }

    config_2x2 = {
            'block': {
                '2x2': {
                    'A1': {'x': 1},
                },
            },
    }
    assert wells_from_config(config_2x2) == {
            (0,0): {'x': 1},
            (0,1): {'x': 1},
            (1,0): {'x': 1},
            (1,1): {'x': 1},
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
            (0,0): {'x': 1},
            (1,1): {'x': 2},
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
            (0,0): {'x': 1, 'y': 1},
            (0,1): {'x': 1        },
            (1,0): {        'y': 1},
    }

def test_block_range():
    config_1x2 = {
            'block': {
                '2x1': {
                    'A1,C1': {'x': 1},
                },
            },
    }
    assert wells_from_config(config_1x2) == {
            (0,0): {'x': 1},
            (0,1): {'x': 1},
            (2,0): {'x': 1},
            (2,1): {'x': 1},
    }

    config_1x2 = {
            'block': {
                '2x1': {
                    'A1,A5,...,A9': {'x': 1},
                },
            },
    }
    assert wells_from_config(config_1x2) == {
            (0,0): {'x': 1},
            (0,1): {'x': 1},
            (0,4): {'x': 1},
            (0,5): {'x': 1},
            (0,8): {'x': 1},
            (0,9): {'x': 1},
    }

def test_one_row_col():
    config = {
            'row': {
                '1': {'x': 1},
            },
            'col': {
                '1': {'y': 1},
            },
    }
    with raises(ConfigError, match='1'):
        wells_from_config(config)

    config = {
            'row': {
                'A': {'x': 1},
            },
            'col': {
                'A': {'y': 1},
            },
    }
    with raises(ConfigError, match='A'):
        wells_from_config(config)

    config = {
            'row': {
                'A': {'x': 1},
            },
            'col': {
                '1': {'y': 1},
            },
    }
    assert wells_from_config(config) == {
            (0,0): {'x': 1, 'y': 1},
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
            (0,0): {'x': 1, 'y': 1},
            (1,0): {'x': 2, 'y': 1},
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
            (0,0): {'x': 1, 'y': 1},
            (0,1): {'x': 1, 'y': 2},
    }

def test_row_range():
    config = {
            'row': {
                'A,C': {'x': 1},
            },
            'col': {
                '1': {'y': 1},
            },
    }
    assert wells_from_config(config) == {
            (0,0): {'x': 1, 'y': 1},
            (2,0): {'x': 1, 'y': 1},
    }

    config = {
            'row': {
                'A,B,...,C': {'x': 1},
            },
            'col': {
                '1': {'y': 1},
            },
    }
    assert wells_from_config(config) == {
            (0,0): {'x': 1, 'y': 1},
            (1,0): {'x': 1, 'y': 1},
            (2,0): {'x': 1, 'y': 1},
    }

def test_col_range():
    config = {
            'row': {
                'A': {'x': 1},
            },
            'col': {
                '1,3': {'y': 1},
            },
    }
    assert wells_from_config(config) == {
            (0,0): {'x': 1, 'y': 1},
            (0,2): {'x': 1, 'y': 1},
    }

    config = {
            'row': {
                'A': {'x': 1},
            },
            'col': {
                '1,2,...,3': {'y': 1},
            },
    }
    assert wells_from_config(config) == {
            (0,0): {'x': 1, 'y': 1},
            (0,1): {'x': 1, 'y': 1},
            (0,2): {'x': 1, 'y': 1},
    }

def test_row_without_col():
    config = {
            'row': {
                'A': {'x': 1},
            },
    }
    with raises(ConfigError, match="row"):
        wells_from_config(config)

    config = {
            'well': {
                'A1': {'y': 1},
            },
            'row': {
                'A': {'x': 1},
            },
    }
    assert wells_from_config(config) == {
            (0,0): {'x': 1, 'y': 1},
    }


def test_col_without_row():
    config = {
            'col': {
                '1': {'y': 1},
            },
    }
    with raises(ConfigError, match="col"):
        wells_from_config(config)

    config = {
            'well': {
                'A1': {'x': 1},
            },
            'col': {
                '1': {'y': 1},
            },
    }
    assert wells_from_config(config) == {
            (0,0): {'x': 1, 'y': 1},
    }

def test_interleaved_row():
    config = {
            'irow': {
                'A': {'x': 1},
            },
            'col': {
                '1': {'y': 1},
                '2': {'y': 2},
                '3': {'y': 3},
                '4': {'y': 4},
            },
    }
    assert wells_from_config(config) == {
            (0,0): {'x': 1, 'y': 1},
            (1,1): {'x': 1, 'y': 2},
            (0,2): {'x': 1, 'y': 3},
            (1,3): {'x': 1, 'y': 4},
    }

    config = {
            'irow': {
                'B': {'x': 2},
            },
            'col': {
                '1': {'y': 1},
                '2': {'y': 2},
                '3': {'y': 3},
                '4': {'y': 4},
            },
    }
    assert wells_from_config(config) == {
            (1,0): {'x': 2, 'y': 1},
            (0,1): {'x': 2, 'y': 2},
            (1,2): {'x': 2, 'y': 3},
            (0,3): {'x': 2, 'y': 4},
    }

def test_interleaved_col():
    config = {
            'row': {
                'A': {'x': 1},
                'B': {'x': 2},
                'C': {'x': 3},
                'D': {'x': 4},
            },
            'icol': {
                '1': {'y': 1},
            },
    }
    assert wells_from_config(config) == {
            (0,0): {'x': 1, 'y': 1},
            (1,1): {'x': 2, 'y': 1},
            (2,0): {'x': 3, 'y': 1},
            (3,1): {'x': 4, 'y': 1},
    }

    config = {
            'row': {
                'A': {'x': 1},
                'B': {'x': 2},
                'C': {'x': 3},
                'D': {'x': 4},
            },
            'icol': {
                '2': {'y': 2},
            },
    }
    assert wells_from_config(config) == {
            (0,1): {'x': 1, 'y': 2},
            (1,0): {'x': 2, 'y': 2},
            (2,1): {'x': 3, 'y': 2},
            (3,0): {'x': 4, 'y': 2},
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
            'expt': {'x': 1},
            'well': {'A1': {}},
    }
    assert wells_from_config(config) == {
            (0,0): {'x': 1},
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
            'expt': {
                'a': 5, 'b': 5, 'c': 5, 'd': 5, 'e': 5,
            },
    }
    wells = wells_from_config(config)
    assert wells[0,0] == {
            'a': 1,
            'b': 2,
            'c': 3,
            'd': 4,
            'e': 5,
    }

def test_block_precedence():
    # For block of different size: smaller blocks have higher precedence.
    config = {
            'block': {
                '2x2': {
                    'A1': {'p': '2x2'},
                },
                '2x1': {
                    'A1': {'p': '2x1'},
                },
                '1x1': {
                    'A1': {'p': '1x1'},
                },
            },
    }
    wells = wells_from_config(config)
    assert wells == {
            (0, 0): {'p': '1x1'},
            (0, 1): {'p': '2x1'},
            (1, 0): {'p': '2x2'},
            (1, 1): {'p': '2x2'},
    }

    # For blocks of the same size, the block defined later has precedence.

    config = {
            'block': {
                '2x1': {
                    'A1': {'p': '2x1'},
                },
                '1x2': {
                    'A1': {'p': '1x2'},
                },
            },
    }
    wells = wells_from_config(config)
    assert wells == {
            (0, 0): {'p': '1x2'},
            (0, 1): {'p': '2x1'},
            (1, 0): {'p': '1x2'},
    }



def test_multi_letter_well():
    config = {
            'well': {
                'AA1': {'x': 1},
            },
    }
    assert wells_from_config(config) == {
            (26,0): {'x': 1},
    }

    config = {
            'well': {
                'AA01': {'x': 1},
            },
    }
    assert wells_from_config(config) == {
            (26,0): {'x': 1},
    }

def test_redundant_well_names():
    config = {
            'well': {
                'A1': {'x': 1},
                'A01': {'y': 1},
            },
    }
    with raises(ConfigError, match='[well.(A1|A01)]'):
        wells_from_config(config)

    config = {
            'row': {
                'A': {},
            },
            'col': {
                '1': {'x': 1},
                '1,2': {'y': 1},
            },
    }
    assert wells_from_config(config) == {
            (0,0): {'x': 1, 'y': 1},
            (0,1): {        'y': 1},
    }

    config = {
            'row': {
                'A': {'x': 1},
                'A,B': {'y': 1},
            },
            'col': {
                '1': {},
            },
    }
    assert wells_from_config(config) == {
            (0,0): {'x': 1, 'y': 1},
            (1,0): {        'y': 1},
    }
