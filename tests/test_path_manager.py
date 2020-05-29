#!/usr/bin/env python3

from wellmap import *
from pathlib import Path
from pytest import raises

DIR = Path(__file__).parent/'toml'

def test_check_overspecified():
    pm = PathManager('a.dat', {'a': 'a.dat'}, DIR/'z.toml')

    with raises(ConfigError, match="ambiguous"):
        pm.get_index_for_only_plate()
    with raises(ConfigError, match="ambiguous"):
        pm.check_named_plates(['a'])

def test_check_named_plates():
    pm0 = PathManager(None, {}, DIR/'z.toml')
    pm1 = PathManager(None, {'a': 'a.dat'}, DIR/'z.toml')
    pm2 = PathManager(None, {'a': 'a.dat', 'b': 'b.dat'}, DIR/'z.toml')

    # These should not raise:
    pm0.check_named_plates([])
    pm1.check_named_plates(['a'])
    pm2.check_named_plates(['a', 'b'])

    # These should raise:
    with raises(ConfigError, match="('a')"):
        pm0.check_named_plates(['a'])
    with raises(ConfigError, match="()"):
        pm1.check_named_plates([])
    with raises(ConfigError, match="('b')"):
        pm1.check_named_plates(['b'])
    with raises(ConfigError, match="('a', 'b')"):
        pm1.check_named_plates(['a', 'b'])
    with raises(ConfigError, match="()"):
        pm2.check_named_plates([])
    with raises(ConfigError, match="('a')"):
        pm2.check_named_plates(['a'])
    with raises(ConfigError, match="('b')"):
        pm2.check_named_plates(['b'])
    with raises(ConfigError, match="('a', 'b', 'c')"):
        pm2.check_named_plates(['a', 'b', 'c'])

    # Path instead of plates:
    pm = PathManager('a.dat', None, DIR/'z.toml')
    with raises(ConfigError, match="()"):
        pm.check_named_plates([])

def test_str():
    # These shouldn't raise.
    str(PathManager('a.dat', {}, DIR/'z.toml'))
    str(PathManager(None, {'a': 'a.dat'}, DIR/'z.toml'))
    str(PathManager(None, {'a': 'a.dat', 'b': 'b.dat'}, DIR/'z.toml'))


def test_index_for_only_plate():
    pm = PathManager('a.dat', None, DIR/'z.toml')
    assert pm.get_index_for_only_plate() == {'path': DIR/'a.dat'}

    # `z.dat` doesn't exist.
    pm = PathManager('z.dat', None, DIR/'z.toml')
    with raises(ConfigError, match="z.dat"):
        pm.get_index_for_only_plate()

def test_index_for_only_plate__ambiguous():
    # Don't need `paths` to be specified; it's ambiguous to even be defined.
    pm = PathManager(None, {}, DIR/'z.toml')
    with raises(ConfigError, match="()"):
        pm.get_index_for_only_plate()

    pm = PathManager(None, {'a': 'a.dat'}, DIR/'z.toml')
    with raises(ConfigError, match="(a)"):
        pm.get_index_for_only_plate()

def test_index_for_only_plate__guess_path():
    pm = PathManager(None, None, DIR/'a.toml', '{0.stem}.dat')
    assert pm.get_index_for_only_plate() == {'path': DIR/'a.dat'}

    # `z.dat` doesn't exist.
    pm = PathManager(None, None, DIR/'z.toml', '{0.stem}.dat')
    with raises(ConfigError, match="z.dat"):
        pm.get_index_for_only_plate()

def test_index_for_only_plate__no_path():
    pm = PathManager(None, None, DIR/'z.toml')
    assert pm.get_index_for_only_plate() == {}

def test_index_for_named_plate__dict():
    pm = PathManager(None, {'a': 'a.dat', 'b': 'b.dat'}, DIR/'z.toml')
    assert pm.get_index_for_named_plate('a') == {'plate': 'a', 'path': DIR/'a.dat'}
    assert pm.get_index_for_named_plate('b') == {'plate': 'b', 'path': DIR/'b.dat'}

    with raises(ConfigError, match="'c'"):
        pm.get_index_for_named_plate('c')

def test_index_for_named_plate__str():
    pm = PathManager(None, '{}.dat', DIR/'z.toml')
    assert pm.get_index_for_named_plate('a') == {'plate': 'a', 'path': DIR/'a.dat'}
    assert pm.get_index_for_named_plate('b') == {'plate': 'b', 'path': DIR/'b.dat'}

    with raises(ConfigError, match="'c'"):
        pm.get_index_for_named_plate('c')

def test_index_for_named_plate__no_paths():
    pm = PathManager(None, None, DIR/'z.toml')
    assert pm.get_index_for_named_plate('a') == {'plate': 'a'}
    assert pm.get_index_for_named_plate('b') == {'plate': 'b'}

def test_index_for_named_plate__unknown_type():
    pm = PathManager(None, ['a'], DIR/'z.toml')
    with raises(ConfigError, match="list"):
        pm.get_index_for_named_plate('a')

