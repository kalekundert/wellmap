#!/usr/bin/env python3

import wellmap
import pytest
import matplotlib.pyplot as plt

from pathlib import Path
from matplotlib.colors import to_rgb
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
        schema=cast(bg=to_rgb)
)
def test_choose_foreground_color(bg, fg):
    assert wellmap.plot.choose_foreground_color(bg) == fg

def test_style_init_signature():
    from inspect import signature
    assert str(signature(Style)) == (
            "(*, "
            "cell_size: float = 0.25, "
            "pad_width: float = 0.2, "
            "pad_height: float = 0.2, "
            "bar_width: float = 0.15, "
            "bar_pad_width: float = 0.2, "
            "top_margin: float = 0.5, "
            "left_margin: float = 0.5, "
            "right_margin: float = 0.2, "
            "bottom_margin: float = 0.2, "
            "color_scheme: str = 'rainbow', "
            "superimpose_values: bool = False, "
            "superimpose_format: str = '', "
            "superimpose_kwargs: dict = {}, "
            "by_param: Dict[str, dict] = {})"
    )

@parametrize_from_file(
        schema=[
            with_wellmap.error_or('value'),
            cast(value=with_py.eval),
        ]
)
def test_style_attr(attr, value, error):
    s0 = Style()
    with error:
        assert getattr(s0, attr) != value

    with error:
        s1 = Style(**{attr: value})
        assert getattr(s1, attr) == value

    s2 = Style()
    with error:
        setattr(s2, attr, value)
        assert getattr(s2, attr) == value

def test_style_attr_normal_syntax():
    s = Style(cell_size=1)
    assert s.cell_size == 1

    s.cell_size = 2
    assert s.cell_size == 2

@parametrize_from_file(
        schema=[
            with_wellmap.error_or('value'),
            cast(value=with_py.eval),
        ]
)
def test_style_attr_by_param(attr, value, error):
    s0 = Style()
    with error:
        assert getattr(s0['x'], attr) != value
    with error:
        assert getattr(s0['y'], attr) != value

    with error:
        s1 = Style(by_param={'x': {attr: value}})
        assert getattr(s1['x'], attr) == value
        assert getattr(s1['y'], attr) != value

    s2 = Style()
    with error:
        setattr(s2['x'], attr, value)
        assert getattr(s1['x'], attr) == value
        assert getattr(s1['y'], attr) != value

def test_style_merge():
    s1 = Style(pad_width=1)
    s2 = Style(pad_width=2, pad_height=2)

    s3 = Style.from_merge(s1, s2)
    assert s1.pad_width == 1
    assert s2.pad_width == 2
    assert s2.pad_height == 2
    assert s3.pad_width == 1
    assert s3.pad_height == 2

    s1.merge(s2)
    assert s1.pad_width == 1
    assert s1.pad_height == 2
    assert s2.pad_width == 2
    assert s2.pad_height == 2

def test_style_merge_defaults():
    # User-specified values should override default values...
    s1 = Style()

    x = s1.cell_size
    y = 2 * x

    s2 = Style(cell_size=y)

    assert s1.cell_size == x
    assert s2.cell_size == y

    s1.merge(s2)

    assert s1.cell_size == y

    # ...but should not override other user-specified values that just happen 
    # to match the default.

    s1 = Style(cell_size=x)

    assert s1.cell_size == x
    assert s2.cell_size == y

    s1.merge(s2)

    assert s1.cell_size == x

def test_style_merge_by_param():
    s1 = Style(color_scheme='g')

    s2 = Style()
    s2['x'].color_scheme = 'x'
    s2.merge(s1)

    assert s2.color_scheme == 'g'
    assert s2['x'].color_scheme == 'x'
    assert s2['y'].color_scheme == 'g'

    s1 = Style()
    s1['y'].color_scheme = 'y'

    s2 = Style()
    s2['x'].color_scheme = 'x'
    s2.merge(s1)

    assert s2.color_scheme == 'rainbow'
    assert s2['x'].color_scheme == 'x'
    assert s2['y'].color_scheme == 'y'

def test_style_merge_dict():
    s1 = Style()
    s1.superimpose_kwargs['x'] = 1
    s1.superimpose_kwargs['y'] = 1

    s2 = Style()
    s2.superimpose_kwargs['y'] = 2
    s2.superimpose_kwargs['z'] = 2
    s2.merge(s1)
    assert s2.superimpose_kwargs == dict(x=1, y=2, z=2)

    s2 = Style()
    s2.superimpose_kwargs = {'y': 2, 'z': 2}
    s2.merge(s1)
    assert s2.superimpose_kwargs == dict(x=1, y=2, z=2)

    s2 = Style(superimpose_kwargs={'y': 2, 'z': 2})
    s2.merge(s1)
    assert s2.superimpose_kwargs == dict(x=1, y=2, z=2)

    s2 = Style()
    s2.superimpose_kwargs = {'y': 2, 'z': 2}
    s2.merge(s1)
    assert s2.superimpose_kwargs == dict(x=1, y=2, z=2)

def test_style_eq():
    assert Style() == Style()

    s1 = Style(); s1.cell_size = 1
    s2 = Style(cell_size=1)
    s3 = Style(cell_size=2)
    assert s1 == s2
    assert s1 != s3

    s1 = Style()
    s2 = Style(cell_size=s1.cell_size)
    assert s1 == s2

    s1 = Style(); s1['x'].color_scheme = 'x'
    s2 = Style(by_param={'x': {'color_scheme': 'x'}})
    s3 = Style(by_param={'x': {'color_scheme': 'y'}})
    s4 = Style(by_param={'y': {'color_scheme': 'x'}})
    assert s1 == s2
    assert s1 != s3
    assert s1 != s4

    s1 = Style()
    s2 = Style(); s2['x'].color_scheme = s1.color_scheme
    assert s1 == s2

@parametrize_from_file(
        schema=defaults(expected=None),
)
def test_style_repr(style, expected):
    expected = expected or style
    style = with_wellmap.eval(style)
    assert repr(style) == expected

def test_style_repr_mutable_defaults():
    s = Style()
    s.superimpose_kwargs['color'] = 'red'
    assert repr(s) == "Style(superimpose_kwargs={'color': 'red'})"

    s.superimpose_kwargs = {'color': 'blue'}
    assert repr(s) == "Style(superimpose_kwargs={'color': 'blue'})"

def test_style_mutable_defaults():
    s1 = Style()
    assert s1.superimpose_kwargs == {}
    assert s1['x'].superimpose_kwargs == {}

    # If we return a fresh dictionary every time, this will fail.
    s1.superimpose_kwargs['color'] = 'red'
    assert s1.superimpose_kwargs == {'color': 'red'}
    assert s1['x'].superimpose_kwargs == {'color': 'red'}

    # If we use class-level mutable objects, other instances may be affected.
    s2 = Style()
    assert s2.superimpose_kwargs == {}
    assert s2['x'].superimpose_kwargs == {}

@parametrize_from_file(
        schema=[
            style,
            cast(tol=float),
            with_wellmap.error_or('expected', 'tol'),
            defaults(params=[], tol=10),
        ],
        indirect=['layout'],
)
def test_show(layout, params, style, tol, expected, error):
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
            style_cli,
            cast(tol=float),
            with_wellmap.error_or('expected', 'tol'),
            # When running on CI, I get RMS values of 2-8. 
            defaults(params=[], tol=10),
        ],
        indirect=['layout'],
)
def test_cli(layout, params, style_argv, expected, tol, error, tmp_path):
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

    cmd += style_argv

    run_cli(cmd, stdout)
    if not error:
        compare_images(expected, actual, TEST_IMAGES, tol=tol)

    plt.close()


