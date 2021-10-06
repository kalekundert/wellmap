#!/usr/bin/env python3

import pytest

from wellmap import *
from pytest import raises
from .param_helpers import *

def test_check_overspecified(tmp_path):
    pm = PathManager('a.dat', {'a': 'a.dat'}, tmp_path/'z.toml')

    with raises(ConfigError, match="ambiguous"):
        pm.get_index_for_only_plate()
    with raises(ConfigError, match="ambiguous"):
        pm.check_named_plates(['a'])

def test_check_named_plates(tmp_path):
    pm0 = PathManager(None, {}, tmp_path / 'z.toml')
    pm1 = PathManager(None, {'a': 'a.dat'}, tmp_path/'z.toml')
    pm2 = PathManager(None, {'a': 'a.dat', 'b': 'b.dat'}, tmp_path/'z.toml')

    # These should not raise:
    pm0.check_named_plates([])
    pm1.check_named_plates(['a'])
    pm2.check_named_plates(['a', 'b'])

    # These should raise:
    with raises(ConfigError, match=r"\('a'\)"):
        pm0.check_named_plates(['a'])
    with raises(ConfigError, match=r"\(\)"):
        pm1.check_named_plates([])
    with raises(ConfigError, match=r"\('b'\)"):
        pm1.check_named_plates(['b'])
    with raises(ConfigError, match=r"\('a', 'b'\)"):
        pm1.check_named_plates(['a', 'b'])
    with raises(ConfigError, match=r"\(\)"):
        pm2.check_named_plates([])
    with raises(ConfigError, match=r"\('a'\)"):
        pm2.check_named_plates(['a'])
    with raises(ConfigError, match=r"\('b'\)"):
        pm2.check_named_plates(['b'])
    with raises(ConfigError, match=r"\('a', 'b', 'c'\)"):
        pm2.check_named_plates(['a', 'b', 'c'])

    # Path instead of plates:
    pm = PathManager('a.dat', None, tmp_path/'z.toml')
    with raises(ConfigError, match="()"):
        pm.check_named_plates([])

def test_str(tmp_path):
    # These shouldn't raise.
    str(PathManager('a.dat', {}, tmp_path/'z.toml'))
    str(PathManager(None, {'a': 'a.dat'}, tmp_path/'z.toml'))
    str(PathManager(None, {'a': 'a.dat', 'b': 'b.dat'}, tmp_path/'z.toml'))

@parametrize_from_file(
        schema=Schema({
            Optional('files', default={}): {str: str},
            'manager': str,
            **with_wellmap.error_or({
                'expected': dict,
            }),
        }),
        indirect=['files'],
)
def test_index_for_only_plate(files, manager, expected, error):
    manager = with_wellmap.copy().use(DIR=files).eval(manager)
    expected = Namespace(DIR=files).eval(expected)
    with error:
        assert manager.get_index_for_only_plate() == expected

@parametrize_from_file(
        schema=Schema({
            Optional('files', default={}): {str: str},
            'manager': str,
            Optional('expected', default={}): dict,
            Optional('errors', default={}): dict,
        }),
        indirect=['files'],
)
def test_index_for_named_plate(files, manager, expected, errors, subtests):
    manager = with_wellmap.copy().use(DIR=files).eval(manager)
    expected = Namespace(DIR=files).eval(expected)

    for key, value in expected.items():
        with subtests.test(plate=key):
            assert manager.get_index_for_named_plate(key) == value

    for key, value in errors.items():
        with subtests.test(plate=key):
            with with_wellmap.error(value):
                manager.get_index_for_named_plate(key)
