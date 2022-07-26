#!/usr/bin/env python3

import wellmap
from pytest_unordered import unordered
from .param_helpers import *

class MockPathManager:

    def check_named_plates(self, names):
        pass

    def get_index_for_only_plate(self):
        return {'path': '/path/to/data'}

    def get_index_for_named_plate(self, name):
        return {'plate': name, 'path': f'/path/to/{name.lower()}'}

@parametrize_from_file(
        schema=[
            cast(config=with_py.eval, expected=with_nan.eval),
            with_wellmap.error_or('expected'),
        ]
)
def test_table_from_config(config, expected, error):
    with error:
        df = wellmap.table_from_config(config, MockPathManager())
        assert df.to_dict('records') == unordered(expected)

