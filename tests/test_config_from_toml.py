#!/usr/bin/env python3

import pytest

from wellmap import *
from pytest_unordered import unordered
from .param_helpers import *

@parametrize_from_file(
        schema=Schema({
            'files': {str: str},
            Optional('kwargs', default={}): with_py.eval,
            **with_wellmap.error_or({
                Optional('config', default={}): with_py.eval,
                Optional('concats', default=[]): list,
                Optional('extras', default={}): with_py.eval,
                Optional('deps', default=[]): list,
                Optional('alerts', default=[]): [{'path': str, 'message': str}],
            }),
        }),
        indirect=['files'],
)
def test_config_from_toml(files, kwargs, config, concats, extras, deps, alerts, error, tmp_path, capsys):
    concats = [
            Namespace(DIR=tmp_path).eval(x)
            for x in concats
    ]

    if deps:
        deps = {tmp_path / p for p in deps}
    else:
        deps = set(tmp_path.glob('*.toml'))

    for alert in alerts:
        alert['path'] = tmp_path / alert['path']

    with error:
        config_out, _, concats_out, extras_out, deps_out = \
                config_from_toml(tmp_path / 'main.toml', **kwargs)

        stderr = capsys.readouterr().err
        concats_out = [x.to_dict('records') for x in concats_out]

        assert config_out == {**config, **extras}
        assert concats_out == unordered(concats)
        assert extras_out == extras
        assert deps_out == deps

        # Test the default alert handler:
        for alert in alerts:
            assert alert['path'].name in stderr
            assert alert['message'] in stderr

        # Test a custom alert handler:
        if alerts:
            actual_alerts = []
            def on_alert(toml_path, message):
                actual_alerts.append({'path': toml_path, 'message': message})

            config_from_toml(tmp_path / 'main.toml', on_alert=on_alert)
            assert actual_alerts == alerts



