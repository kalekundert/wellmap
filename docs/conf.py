import wellmap

import sys, os
sys.path.append(os.path.dirname(__file__))  # custom sphinx extensions

import sphinx.ext.autosummary
sphinx.ext.autosummary.WELL_KNOWN_ABBREVIATIONS = ('i.e.', 'e.g.')

source_suffix = '.rst'
master_doc = 'index'
project = u'wellmap'
copyright = u'2015, Kale Kundert'
version = wellmap.__version__
release = wellmap.__version__
exclude_patterns = ['_build', '.*', 'venv', 'slides', 'drafts']
templates_path = ['_templates']
html_static_path = ['_static']

extensions = [
        '_ext.example',
        '_ext.hidden_section',
        'sphinx.ext.autodoc',
        'sphinx.ext.autosummary',
        'sphinx.ext.intersphinx',
        'sphinx.ext.napoleon',
        'sphinx.ext.viewcode',
        'sphinxcontrib.programoutput',
        'sphinx_issues',
        'myst_parser',
]
autodoc_default_options = {
        'members': True,
        'special-members': True,
        'exclude-members': '__hash__,__weakref__,__getattribute__,__getattr__,__setattr__'
}
intersphinx_mapping = {
        'python': ('https://docs.python.org/3', None),
        'pd': ('https://pandas.pydata.org/pandas-docs/stable/', None),
        'mpl': ('https://matplotlib.org/', None),
}
default_role = 'any'
add_function_parentheses = True
pygments_style = 'sphinx'
autosummary_generate = True
issues_github_path = 'kalekundert/wellmap'
rst_epilog = """\
.. |well| replace:: :ref:`well <well>`
.. |block| replace:: :ref:`block <block>`
.. |row| replace:: :ref:`row <row>`
.. |col| replace:: :ref:`col <col>`
.. |irow| replace:: :ref:`irow <irow>`
.. |icol| replace:: :ref:`icol <icol>`
.. |plate| replace:: :ref:`plate <plate>`
.. |expt| replace:: :ref:`expt <expt>`
.. |extras| replace:: :ref:`extras <extras>`

.. _tidy: https://www.jstatsoft.org/article/view/v059i10
.. _issue: https://github.com/kalekundert/wellmap/issues
.. _pull requests: https://github.com/kalekundert/wellmap/pulls 
"""

from sphinx_rtd_theme import get_html_theme_path
html_theme = "sphinx_rtd_theme"
html_theme_path = [get_html_theme_path()]
html_theme_options = {}

def setup(app):
    app.add_js_file('js/tweaks.js')
    app.add_css_file('css/tweaks.css')

    app.add_crossref_type(
            'prog',
            'prog',
            objname='command-line program',
            indextemplate='pair: %s; command-line program',
    )
