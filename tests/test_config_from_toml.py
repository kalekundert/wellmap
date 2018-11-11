#!/usr/bin/env python3

from bio96 import *
from pathlib import Path

DIR = Path(__file__).parent/'toml'

def test_one_include():
    config, paths = config_from_toml(DIR/'one_include.toml')
    assert config == {
            'well': {
                'A1': {'x': 1, 'y': 1},
            },
    }

def test_alert(capsys):
    config, paths = config_from_toml(DIR/'alert.toml')
    assert capsys.readouterr().out == "Hello world!\n"




