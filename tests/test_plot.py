#!/usr/bin/env python3

import wellmap
import pytest
import matplotlib.pyplot as plt

from pathlib import Path
from .param_helpers import *

TEST = Path(__file__).parent
REF_IMAGES = TEST / 'images/ref'
TEST_IMAGES = TEST / 'images/test'

def run_cli(cmd, out='Layout written'):
    import sys, re, shlex
    from io import StringIO
    from contextlib import contextmanager, redirect_stdout

    @contextmanager
    def spoof_argv(argv):
        try:
            orig_argv = sys.argv
            sys.argv = [str(x) for x in argv]
            yield
        finally:
            sys.argv = orig_argv

    stdout = StringIO()
    with redirect_stdout(stdout):
        with spoof_argv(cmd):
            wellmap.plot.main()

    if out is None:
        return
    if isinstance(out, str):
        out = [out]
    for expected in out:
        assert expected in stdout.getvalue()


@parametrize_from_file(
        schema=Schema({
            'df': [{str: with_py.eval}],
            'attrs': with_py.eval,
            **with_wellmap.error_or({
                'expected': [str],
            }),
        })
)
def test_pick_attrs(df, attrs, expected, error):
    df = pd.DataFrame(df)
    with error:
        assert wellmap.plot.pick_attrs(df, attrs) == expected

@parametrize_from_file(
        schema=Schema({
            'layout': str,
            Optional('attrs', default=[]): Or(str, [str]),
            Optional('color', default='rainbow'): str,
            **with_wellmap.error_or({
                'expected': str,
                # When running on CI, I get RMS values of 2-8. 
                Optional('tol', default=10): Coerce(float),
            }),
        }),
        indirect=['layout'],
)
def test_show(layout, attrs, color, tol, expected, error):
    if not error:
        actual = layout.parent / expected
        expected = REF_IMAGES / expected

    with error:
        fig = show(layout, attrs, color)
        fig.savefig(actual)
        compare_images(expected, actual, TEST_IMAGES, tol=tol)

    plt.close()

@parametrize_from_file(
        key='test_show',
        schema=Schema({
            'layout': str,
            Optional('attrs', default=[]): Or(str, [str]),
            Optional('color', default='rainbow'): str,
            **with_wellmap.error_or({
                'expected': str,
                # When running on CI, I get RMS values of 2-8. 
                Optional('tol', default=10): Coerce(float),
            }),
        }),
        indirect=['layout'],
)
def test_cli(layout, attrs, color, expected, tol, error, tmp_path):
    cmd = ['wellmap', layout]

    if error:
        cmd += ['-f']
        stdout = error.messages
    else:
        actual = layout.parent / expected
        expected = REF_IMAGES / expected
        cmd += ['-o', actual]
        stdout = 'Layout written' 

    if attrs:
        cmd += ([attrs] if isinstance(attrs, str) else attrs)
    if color:
        cmd += ['-c', color]

    run_cli(cmd, stdout)
    if not error:
        compare_images(expected, actual, TEST_IMAGES, tol=tol)

    plt.close()

