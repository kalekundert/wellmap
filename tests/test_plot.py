#!/usr/bin/env python3

import wellmap
import pytest
from pathlib import Path

# These tests are pretty minimal.  Mostly just testing either that it doesn't 
# crash or that it crashes with the right error.  The resulting images are 
# written out as *.pdf files, so you can look at those by hand if you want to 
# be sure the plots are correct (which is *not* tested).

DIR = Path(__file__).parent / 'plot'

def run_cli(args, out='Layout written'):
    import sys, re, shlex
    from io import StringIO
    from contextlib import contextmanager, redirect_stdout

    @contextmanager
    def spoof_argv(*args):
        try:
            orig_argv = sys.argv
            sys.argv = args
            yield
        finally:
            sys.argv = orig_argv

    stdout = StringIO()
    with redirect_stdout(stdout):
        with spoof_argv('wellmap', '-o', f'{DIR}/$.pdf', *shlex.split(str(args))):
            wellmap.plot.main()

    if out is None:
        return
    if isinstance(out, str):
        out = [out]
    for expected in out:
        assert re.search(expected, stdout.getvalue())


def test_no_wells():
    run_cli(DIR/'no_wells.toml', [
        "no_wells.toml",
        "No wells defined",
    ])

def test_no_attr():
    run_cli(DIR/'no_attrs.toml', "No attributes defined.")

def test_degenerate_attr():
    run_cli(DIR/'degenerate_attr.toml', [
        "degenerate attributes",
        ": 'x'",
    ])

def test_unknown_attr():
    run_cli(f'{DIR}/one_attr.toml XXX', [
        "one_attr.toml",
        "No such attribute: 'XXX'",
        "Did you mean: 'x'",
    ])

    # Make sure the fancy plural logic works :-)
    run_cli(f'{DIR}/one_attr.toml XXX YYY', [
        "one_attr.toml",
        "No such attributes: 'XXX', 'YYY'",
        "Did you mean: 'x'",
    ])

def test_one_attr():
    run_cli(DIR/'one_attr.toml')

def test_two_attrs():
    run_cli(DIR/'two_attrs.toml')

def test_user_attr():
    run_cli(f'{DIR}/two_attrs.toml x')
    run_cli(f'{DIR}/two_attrs.toml y')
    run_cli(f'{DIR}/two_attrs.toml x y')

def test_one_value():
    run_cli(f'{DIR}/one_value.toml x')

def test_sort_values():
    run_cli(f'{DIR}/sort_numbers.toml')
    run_cli(f'{DIR}/sort_dates.toml')
    run_cli(f'{DIR}/sort_strings.toml')

def test_nan_first():
    run_cli(DIR/'nan_first.toml')

def test_skip_wells():
    run_cli(DIR/'skip_wells.toml')

def test_long_labels():
    run_cli(DIR/'long_labels.toml')

def test_reasonably_complex():
    run_cli(DIR/'reasonably_complex_2.toml')
    run_cli(DIR/'reasonably_complex_1.toml')

def test_colorscheme():
    run_cli(f'{DIR}/colors_viridis.toml -c viridis')
    run_cli(f'{DIR}/colors_plasma.toml -c plasma')
    run_cli(f'{DIR}/colors_coolwarm.toml -c coolwarm')

