#!/usr/bin/env python3

import wellmap
import pytest
import sys
import re

from pytest_unordered import unordered
from contextlib import nullcontext
from .param_helpers import *

if sys.version_info >= (3, 10, 0):
    from functools import partial
    zip_equal = partial(zip, strict=True)
else:
    from more_itertools import zip_equal

@parametrize_from_file(
        schema=[
            defaults(kwargs={}, deprecated=None),
            with_wellmap.error_or('expected'),
        ],
        indirect=['files'],
)
def test_load(files, kwargs, expected, deprecated, error, subtests):

    def read_csv_check_extras_positional(path, extras):
        assert extras == expected.get('meta', expected)['extras']
        return pd.read_csv(path)

    def read_csv_check_extras_keyword(path, *, extras):
        assert extras == expected.get('meta', expected)['extras']
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
    if not isinstance(kwargs, list):
        kwargs = [kwargs]

    expected = Namespace(with_py, DIR=files).eval(expected)
    meta = expected.get('meta', {})
    if 'style' in meta or 'param_styles' in meta:
        meta['style'] = wellmap.Style(
                **meta.pop('style', {}),
                by_param=meta.pop('param_styles', {}),
        )

    if deprecated:
        deprecated = pytest.deprecated_call(match=re.escape(deprecated))
    else:
        deprecated = nullcontext()

    def compare_df(actual, expected):
        assert actual.to_dict('records') == unordered(expected)

    def compare_deps(actual, expected):
        assert actual == set(expected)

    def compare_extras(actual, expected):
        assert actual == expected

    def compare_meta(actual, expected):
        if 'extras' in expected:
            compare_extras(actual.extras, expected['extras'])
        if 'deps' in expected:
            compare_deps(actual.dependencies, expected['deps'])
        if 'style' in expected:
            assert actual.style == expected['style']

    comparisons = {
            'labels': compare_df,
            'data': compare_df,
            'labels+data': compare_df,
            'meta': compare_meta,
            'deps': compare_deps,
            'extras': compare_extras,
    }

    for kwargs_i in kwargs:
        with subtests.test(kwargs=kwargs_i), error:
            with deprecated:
                out = wellmap.load(files/'main.toml', **kwargs_i)

            if len(expected) == 1:
                out = [out]

            for (key, expected_i), actual in zip_equal(expected.items(), out):
                with subtests.test(retval=key):
                    comparisons[key](actual, expected_i)

