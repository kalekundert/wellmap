#!/usr/bin/env python3

import pytest
from wellmap import get_dotted_key

DEMO = {'a': {'b': 1}, 'c': 2}

def test_empty():
    assert get_dotted_key({}, '') == {}

def test_one_key():
    params = {
            'a': {'b': 1},
            'b': {},
            'c': 2
    }
    for key, value in params.items():
        assert get_dotted_key(DEMO, key) == value

def test_two_keys():
    params = {
            'a.b': 1,
            'a . b': 1,  # TOML allows whitespace.
            'b.x': {},
    }
    for key, value in params.items():
        assert get_dotted_key(DEMO, key) == value

def test_too_many_keys():
    with pytest.raises(AttributeError):
        get_dotted_key(DEMO, 'c.x')
