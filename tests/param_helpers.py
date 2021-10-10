#!/usr/bin/env python3

import pytest, math
import parametrize_from_file

from wellmap import *
from voluptuous import Schema, Optional, And, Or
from parametrize_from_file.voluptuous import Namespace

class ExpectNaN:

    def __eq__(self, other):
        import math
        return math.isnan(other)

with_py = Namespace()
with_nan = Namespace(nan=ExpectNaN())
with_wellmap = Namespace('import wellmap; from wellmap import *; import pandas as pd')

@pytest.fixture
def files(request, tmp_path):
    for name, contents in request.param.items():
        p = tmp_path / name
        p.write_text(contents)

    return tmp_path

