#!/usr/bin/env python3

import os
import shlex

from docutils import nodes
from docutils.statemachine import StringList
from sphinx.util.docutils import SphinxDirective

class Example(SphinxDirective):
    required_arguments = 1
    optional_arguments = 0
    has_content = True
    final_argument_whitespace = True
    option_spec = {
            'attrs': lambda x: x.split(','),
            'colors': lambda x: x,
            'no-figure': lambda x: x,
    }

    def run(self):
        rel_paths = shlex.split(self.arguments[0])
        example_rst = ""

        if not self.content:
            content = [None] * len(rel_paths)
        else:
            content = '\n'.join(self.content).split('--EOF--')

        if len(content) != len(rel_paths):
            raise self.error(f"found {len(content)} TOML snippets, but {len(rel_paths)} paths.")

        for rel_path, content in zip(rel_paths, content):
            toml_path, toml_abs_path = self.env.relfn2path(rel_path)
            svg_path = change_ext(toml_path, '.svg')
            svg_abs_path = change_ext(toml_abs_path, '.svg')
            name = os.path.basename(toml_path)

            if content:
                os.makedirs(os.path.dirname(toml_abs_path), exist_ok=True)
                with open(toml_abs_path, 'w') as f:
                    f.write(content)

            if not os.path.exists(toml_abs_path):
                raise self.error(f"no such file: {toml_path}")

            example_rst += f'''\
.. literalinclude:: /{toml_path}
    :language: toml
    :caption: :download:`{name} </{toml_path}>`
'''

        if 'no-figure' not in self.options:
            import wellmap
            import colorcet
            import matplotlib.pyplot as plt

            df = wellmap.load(toml_abs_path)
            attrs = self.options.get('attrs', [])
            cmap = wellmap.verify.get_colormap(self.options.get('colors', 'rainbow'))
            fig = wellmap.verify.plot_layout(df, attrs, cmap=cmap)
            fig.savefig(svg_abs_path, bbox_inches='tight')

            example_rst += f'''\
.. figure:: /{svg_path}
'''
        example_str_list = StringList(example_rst.splitlines())

        wrapper = nodes.container(classes=['wellmap-example'])
        self.state.nested_parse(example_str_list, 0, wrapper)
        return [wrapper]

def change_ext(path, new_ext):
    return os.path.splitext(path)[0] + new_ext

def setup(app):
    app.add_directive('example', Example)
