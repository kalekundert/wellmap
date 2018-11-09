#!/usr/bin/env python3

from bio96 import *

def test_one_well():
    config = {
            'well': {
                'A1': {'x': 1},
            },
    }
    wells = wells_from_config(config)
    assert wells['A1']['x'] == 1

def test_multiple_wells():
    config = {
            'well': {
                'A1': {'x': 1},
                'B2': {'x': 2},
            },
    }
    wells = wells_from_config(config)
    assert wells['A1']['x'] == 1
    assert wells['B2']['x'] == 2

def test_one_row_col():
    config = {
            'row': {
                'A': {'x': 1},
            },
            'col': {
                '1': {'y': 1},
            },
    }
    wells = wells_from_config(config)
    assert wells['A1']['x'] == 1 and wells['A1']['y'] == 1

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
    wells = wells_from_config(config)
    assert wells['A1']['x'] == 1 and wells['A1']['y'] == 1
    assert wells['B1']['x'] == 2 and wells['B1']['y'] == 1

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
    wells = wells_from_config(config)
    assert wells['A1']['x'] == 1 and wells['A1']['y'] == 1
    assert wells['A2']['x'] == 1 and wells['A2']['y'] == 2

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
    wells = wells_from_config(config)
    assert wells['A1']['x'] == 1 and wells['A1']['y'] == 1
    assert wells['B2']['x'] == 1 and wells['B2']['y'] == 2

    config = {
            'irow': {
                'B': {'x': 2},
            },
            'col': {
                '1': {'y': 1},
                '2': {'y': 2},
            },
    }
    wells = wells_from_config(config)
    assert wells['B1']['x'] == 2 and wells['B1']['y'] == 1
    assert wells['A2']['x'] == 2 and wells['A2']['y'] == 2
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
    wells = wells_from_config(config)
    assert wells['A1']['x'] == 1 and wells['A1']['y'] == 1
    assert wells['B2']['x'] == 2 and wells['B2']['y'] == 1

    config = {
            'row': {
                'A': {'x': 1},
                'B': {'x': 2},
            },
            'icol': {
                '2': {'y': 2},
            },
    }
    wells = wells_from_config(config)
    assert wells['A2']['x'] == 1 and wells['A2']['y'] == 2
    assert wells['B1']['x'] == 2 and wells['B1']['y'] == 2

def test_top_level_params():
    config = {
            'x': 1,
            'well': {'A1': {}},
    }
    wells = wells_from_config(config)
    assert wells['A1']['x'] == 1

