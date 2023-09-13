#!/usr/bin/env python3

import pytest, math, shutil
import parametrize_from_file
import matplotlib.testing

from wellmap import *
from parametrize_from_file import Namespace, cast, defaults, error_or

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
        p.write_text(contents, encoding='utf-8')

    return tmp_path

@pytest.fixture
def layout(request, tmp_path):
    p = tmp_path / 'layout.toml'
    p.write_text(request.param)
    return p

def style(params):
    style = with_py.eval(params.pop('style', {}))
    param_styles = with_py.eval(params.pop('param_styles', {}))
    params['style'] = Style(**style, by_param=param_styles)
    return params

def style_cli(params):
    argv = params['style_argv'] = []
    style = with_py.eval(params.pop('style', {}))
    param_styles = params.pop('param_styles', {})

    try:
        argv += ['-c', style.pop('color_scheme')]
    except KeyError:
        pass

    try:
        if style.pop('superimpose_values', False):
            argv += ['-s']
    except KeyError:
        pass

    if style or param_styles:
        marks = params.setdefault('marks', [])
        marks.append(pytest.mark.skip(f"can't set the following style options via the CLI: {quoted_join(style)}"))

    return params

def dataframe(param_str):
    import pandas as pd
    param_obj = with_py.eval(param_str)
    return pd.DataFrame(param_obj)


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



