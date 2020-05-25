#!/usr/bin/env python3

import os.path
import subprocess

from docutils import nodes
from docutils.statemachine import StringList
from sphinx.util.docutils import SphinxDirective

class Example(SphinxDirective):
    required_arguments = 1
    optional_arguments = 0
    has_content = False
    option_spec = {
            'attrs': lambda x: x.split(','),
    }

    def run(self):
        toml_path, toml_abs_path = self.env.relfn2path(self.arguments[0])
        svg_path = change_ext(toml_path, '.svg')
        svg_abs_path = change_ext(toml_abs_path, '.svg')
        name = os.path.basename(toml_path)

        if not os.path.exists(toml_abs_path):
            raise self.error(f"no such file: {toml_path}")

        import bio96
        import colorcet

        df = bio96.load(toml_abs_path)
        attrs = self.options.get('attrs', [])
        cmap = colorcet.cm['rainbow']
        fig = bio96.verify.plot_layout(df, attrs, cmap=cmap)
        fig.savefig(svg_abs_path)

        example_rst = f'''\
.. literalinclude:: /{toml_path}
    :language: toml
    :caption: :download:`{name} </{toml_path}>`

.. figure:: /{svg_path}
'''
        example_str_list = StringList(example_rst.splitlines())

        wrapper = nodes.paragraph()
        self.state.nested_parse(example_str_list, 0, wrapper)
        return wrapper.children

def change_ext(path, new_ext):
    return os.path.splitext(path)[0] + new_ext

def setup(app):
    app.add_directive('example', Example)
