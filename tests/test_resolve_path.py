#!/usr/bin/env python3

from wellmap import *
from pathlib import Path

def test_relative_path():
    assert resolve_path('a/z.toml', 'b') == Path('a/b')

def test_absolute_path():
    assert resolve_path('a/z.toml', '/b') == Path('/b')
