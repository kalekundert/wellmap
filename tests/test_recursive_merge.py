#!/usr/bin/env python3

from wellmap import *

def test_recursive_merge():
    examples = [
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
    ]
    for a, b, overwrite, x in examples:
        recursive_merge(a, b, overwrite)
        assert a == x

