#!/usr/bin/env python3

import wellmap
from pytest_unordered import unordered
from more_itertools import zip_equal
from .param_helpers import *

@parametrize_from_file(
        schema=Schema({
            'files': dict,
            Optional('kwargs', default={}): dict,
            **with_wellmap.error_or({
                'expected': dict,
            }),
        }),
        indirect=['files'],
)
def test_load(files, kwargs, expected, error, subtests):

    def read_csv_check_extras(path, extras):
        assert extras == expected['extras']
        return pd.read_csv(path)

    with_loaders = Namespace(
            'import pandas as pd',
            read_csv_check_extras=read_csv_check_extras,
    )
    kwargs = with_loaders.eval(kwargs)
    expected = with_py.copy().use(DIR=files).eval(expected)

    def compare_df(actual, expected):
        assert actual.to_dict('records') == unordered(expected)

    def compare_set(actual, expected):
        assert actual == set(expected)

    def compare_dict(actual, expected):
        assert actual == expected

    comparisons = {
            'labels': compare_df,
            'data': compare_df,
            'labels+data': compare_df,
            'deps': compare_set,
            'extras': compare_dict,
    }

    with error:
        out = wellmap.load(files/'main.toml', **kwargs)
        if len(expected) == 1:
            out = [out]

        for (key, expected_i), actual in zip_equal(expected.items(), out):
            with subtests.test(retval=key):
                comparisons[key](actual, expected_i)

