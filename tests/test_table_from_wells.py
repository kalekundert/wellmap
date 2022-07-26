#!/usr/bin/env python3

import wellmap
from pytest_unordered import unordered
from .param_helpers import *

@parametrize_from_file(
        schema=[
            cast(
                wells=with_py.eval(keys=True),
                index=with_py.eval,
                expected=with_nan.eval,
            ),
            defaults(index={}),
        ],
)
def test_table_from_wells(wells, index, expected):
    df = wellmap.table_from_wells(wells, index)
    assert df.to_dict('records') == unordered(expected)

