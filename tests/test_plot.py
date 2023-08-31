#!/usr/bin/env python3

import wellmap
import pytest
import matplotlib.pyplot as plt

from pathlib import Path
from wellmap.util import quoted_join
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
        schema=[
            cast(df=with_py.eval, params=with_py.eval),
            with_wellmap.error_or('expected'),
        ],
)
def test_pick_params(df, params, expected, error):
    df = pd.DataFrame(df)
    with error:
        assert wellmap.plot.pick_params(df, params) == expected

@parametrize_from_file(
        schema=[
            cast(tol=float),
            with_wellmap.error_or('expected', 'tol'),
            defaults(params=[], style={}, tol=10),
        ],
        indirect=['layout'],
)
def test_show(layout, params, style, tol, expected, error):
    style = wellmap.Style(**style)

    with error:
        fig = show(layout, params, style=style)

    if not error:
        actual = layout.parent / expected
        expected = REF_IMAGES / expected

        fig.savefig(actual)
        compare_images(expected, actual, TEST_IMAGES, tol=tol)

    plt.close()

@parametrize_from_file(
        schema=[
            cast(df=dataframe, tol=float),
            with_wellmap.error_or('expected', 'tol'),
            defaults(tol=10),
        ],
)
def test_show_df(df, tol, expected, error, tmp_path):
    # Most of the functionality of the `show_df()` function is tested via the 
    # `show()` function.  The tests here just look at some data frames that 
    # couldn't possibly be generated from a TOML layout (i.e. missing various 
    # well-location columns).

    with error:
        fig = show_df(df)

    if not error:
        actual = tmp_path / expected
        expected = REF_IMAGES / expected

        fig.savefig(actual)
        compare_images(expected, actual, TEST_IMAGES, tol=tol)

    plt.close()

@parametrize_from_file(
        key='test_show',
        schema=[
            cast(tol=float),
            with_wellmap.error_or('expected', 'tol'),
            # When running on CI, I get RMS values of 2-8. 
            defaults(params=[], style={}, tol=10),
        ],
        indirect=['layout'],
)
def test_cli(layout, params, style, expected, tol, error, tmp_path):
    cmd = ['wellmap', layout]

    if error:
        cmd += ['-f']
        stdout = error.messages
    else:
        actual = layout.parent / expected
        expected = REF_IMAGES / expected
        cmd += ['-o', actual]
        stdout = 'Layout written' 

    if params:
        cmd += ([params] if isinstance(params, str) else params)
    if 'color_scheme' in style:
        cmd += ['-c', style.pop('color_scheme')]

    # Skip any tests involving style settings that can't be set via the CLI:
    if style:
        pytest.skip(f"can't set the following style options via the CLI: {quoted_join(style)}")

    run_cli(cmd, stdout)
    if not error:
        compare_images(expected, actual, TEST_IMAGES, tol=tol)

    plt.close()

