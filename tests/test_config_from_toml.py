#!/usr/bin/env python3

import pytest

from wellmap import *
from pytest_unordered import unordered
from .param_helpers import *

@parametrize_from_file(
        schema=[
            style,
            error_or(
                'config', 'concats', 'extras', 'deps', 'alerts',
                globals=with_wellmap,
            ),
            defaults(
                kwargs={},
                config={},
                concats=[],
                extras={},
                deps=[],
                alerts=[],
            ),
        ],
        indirect=['files'],
)
def test_config_from_toml(files, kwargs, config, concats, extras, deps, style, alerts, error, tmp_path, capsys):
    kwargs = with_py.eval(kwargs)
    config = with_py.eval(config)
    extras = with_py.eval(extras)
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
        config_out, _, concats_out, meta_out = \
                config_from_toml(tmp_path / 'main.toml', **kwargs)

        stderr = capsys.readouterr().err
        concats_out = [x.to_dict('records') for x in concats_out]

        assert config_out == {**config, **extras}
        assert concats_out == unordered(concats)
        assert meta_out.extras == extras
        assert meta_out.dependencies == deps
        assert meta_out.style == style

        # Default alert handler:
        for alert in alerts:
            assert alert['path'].name in stderr
            assert alert['message'] in stderr

        # Custom alert handler:
        if alerts:
            actual_alerts = []
            def on_alert(toml_path, message):
                actual_alerts.append({'path': toml_path, 'message': message})

            config_from_toml(tmp_path / 'main.toml', on_alert=on_alert)
            assert actual_alerts == alerts



