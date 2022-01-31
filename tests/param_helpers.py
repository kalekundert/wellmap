#!/usr/bin/env python3

import pytest, math, shutil
import parametrize_from_file
import matplotlib.testing

from wellmap import *
from voluptuous import Schema, Optional, And, Or, Coerce
from parametrize_from_file.voluptuous import Namespace

matplotlib.testing.setup()

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

@pytest.fixture
def layout(request, tmp_path):
    p = tmp_path / 'layout.toml'
    p.write_text(request.param)
    return p


def compare_images(expected, actual, staging_dir, *, tol):
    from matplotlib.testing.compare import compare_images

    if not expected.exists():
        staging_dir.mkdir(exist_ok=True)
        shutil.copy(actual, staging_dir / actual.name)
        pytest.fail(f"Reference image not found: {expected}\nTest image: {staging_dir / actual.name}\nIf the test image looks right, rename it to the above reference path and rerun the test.")

    else:
        diff = compare_images(expected, actual, tol)
        if diff is not None:
            pytest.fail(diff)



