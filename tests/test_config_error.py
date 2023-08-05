#!/usr/bin/env python3

from wellmap import *

def test_str():
    err = LayoutError("x")
    assert str(err) == "x"

    err.toml_path = "y"
    assert str(err) == "y: x"

