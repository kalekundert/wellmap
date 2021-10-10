#!/usr/bin/env python3

import wellmap
from pytest_unordered import unordered
from more_itertools import zip_equal
from .param_helpers import *

@parametrize_from_file(
        schema=Schema({
            'files': dict,
            Optional('kwargs', default={}): Or(dict, list),
            **with_wellmap.error_or({
                'expected': dict,
            }),
        }),
        indirect=['files'],
)
def test_load(files, kwargs, expected, error, subtests):

    def read_csv_check_extras_positional(path, extras):
        assert extras == expected['extras']
        return pd.read_csv(path)

    def read_csv_check_extras_keyword(path, *, extras):
        assert extras == expected['extras']
        return pd.read_csv(path)

    def read_csv_ignore_extras_variable(path, *extras):
        assert not extras
        return pd.read_csv(path)

    def read_csv_ignore_extras_variable_keyword(path, **extras):
        assert not extras
        return pd.read_csv(path)

    with_loaders = Namespace(
            'import pandas as pd',
            read_csv_check_extras=read_csv_check_extras_positional,
            read_csv_check_extras_positional=read_csv_check_extras_positional,
            read_csv_check_extras_keyword=read_csv_check_extras_keyword,
            read_csv_ignore_extras_variable=read_csv_ignore_extras_variable,
            read_csv_ignore_extras_variable_keyword=read_csv_ignore_extras_variable_keyword,
    )
    kwargs = with_loaders.eval(kwargs)
    expected = with_py.copy().use(DIR=files).eval(expected)

    if not isinstance(kwargs, list):
        kwargs = [kwargs]

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

    for kwargs_i in kwargs:
        with subtests.test(kwargs=kwargs_i), error:
            out = wellmap.load(files/'main.toml', **kwargs_i)
            if len(expected) == 1:
                out = [out]

            for (key, expected_i), actual in zip_equal(expected.items(), out):
                with subtests.test(retval=key):
                    comparisons[key](actual, expected_i)

