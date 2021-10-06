#!/usr/bin/env python3

import wellmap
import pytest

@pytest.mark.parametrize(
        'a, b, overwrite, x', [
            ({},              {},              False, {}),
            ({},              {'x': 1},        False, {'x': 1}),
            ({'x': 1},        {'x': 1},        False, {'x': 1}),
            ({'x': 1},        {'y': 1},        False, {'x': 1, 'y': 1}),
            ({'x': 1},        {'x': 2},        False, {'x': 1}),
            ({'x': 1},        {},              False, {'x': 1}),

            ({},              {'x': {'y': 1}}, False, {'x': {'y': 1}}),
            ({'x': 1},        {'x': {'y': 1}}, False, {'x': 1}),
            ({'x': {'y': 1}}, {'x': {'y': 1}}, False, {'x': {'y': 1}}),
            ({'x': {'y': 1}}, {'x': {'z': 1}}, False, {'x': {'y': 1, 'z': 1}}),
            ({'x': {'y': 1}}, {'x': {'y': 2}}, False, {'x': {'y': 1}}),
            ({'x': {'y': 1}}, {'x': 1},        False, {'x': {'y': 1}}),
            ({'x': {'y': 1}}, {},              False, {'x': {'y': 1}}),

            ({},              {},              True,  {}),
            ({},              {'x': 1},        True,  {'x': 1}),
            ({'x': 1},        {'x': 1},        True,  {'x': 1}),
            ({'x': 1},        {'y': 1},        True,  {'x': 1, 'y': 1}),
            ({'x': 1},        {'x': 2},        True,  {'x': 2}),
            ({'x': 1},        {},              True,  {'x': 1}),

            ({},              {'x': {'y': 1}}, True,  {'x': {'y': 1}}),
            ({'x': 1},        {'x': {'y': 1}}, True,  {'x': {'y': 1}}),
            ({'x': {'y': 1}}, {'x': {'y': 1}}, True,  {'x': {'y': 1}}),
            ({'x': {'y': 1}}, {'x': {'z': 1}}, True,  {'x': {'y': 1, 'z': 1}}),
            ({'x': {'y': 1}}, {'x': {'y': 2}}, True,  {'x': {'y': 2}}),
            ({'x': {'y': 1}}, {'x': 1},        True,  {'x': 1}),
            ({'x': {'y': 1}}, {},              True,  {'x': {'y': 1}}),
        ],
)
def test_recursive_merge(a, b, overwrite, x):
    wellmap.recursive_merge(a, b, overwrite)
    assert a == x

