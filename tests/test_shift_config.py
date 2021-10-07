#!/usr/bin/env python3

import wellmap
from .param_helpers import *

@parametrize_from_file(
        schema=Schema({
            'config': with_py.eval,
            'shift': with_py.eval,
            **with_wellmap.error_or({
                'expected': with_py.eval,
            }),
        }),
)
def test_shift_config(config, shift, expected, error):
    with error:
        assert wellmap.shift_config(config, shift) == expected

    assert wellmap.shift_config(config, (0, 0)) == config

