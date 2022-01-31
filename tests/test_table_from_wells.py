#!/usr/bin/env python3

import wellmap
from pytest_unordered import unordered
from .param_helpers import *

@parametrize_from_file(
        schema=Schema({
            'wells': with_py.eval(keys=True),
            Optional('index', default={}): with_py.eval,
            'expected': with_nan.eval,
        }),
)
def test_table_from_wells(wells, index, expected):
    df = wellmap.table_from_wells(wells, index)
    assert df.to_dict('records') == unordered(expected)

