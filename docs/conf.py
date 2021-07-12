import sys, os
import wellmap
sys.path.append(os.path.dirname(__file__))

source_suffix = '.rst'
master_doc = 'index'
project = u'wellmap'
copyright = u'2015, Kale Kundert'
version = wellmap.__version__
release = wellmap.__version__
exclude_patterns = ['_build']
templates_path = ['_templates']
html_static_path = ['_static']

extensions = [
        '_ext.example',
        '_ext.hidden_section',
        #'show_nodes',
        'sphinx.ext.autodoc',
        'sphinx.ext.autosectionlabel',
        'sphinx.ext.autosummary',
        'sphinx.ext.intersphinx',
        'sphinx.ext.napoleon',
        'sphinx.ext.viewcode',
        'sphinxcontrib.programoutput',
        'myst_parser',
]
intersphinx_mapping = {
        'python': ('https://docs.python.org/3', None),
        'pd': ('https://pandas.pydata.org/pandas-docs/stable/', None),
        'mpl': ('https://matplotlib.org/', None),
}
default_role = 'any'
add_function_parentheses = True
pygments_style = 'sphinx'
autosummary_generate = True
rst_epilog = """\
.. |well| replace:: `[well] <[well.A1]>`
.. |block| replace:: `[block] <[block.WxH.A1]>`
.. |row| replace:: `[row] <[row.A]>`
.. |col| replace:: `[col] <[col.1]>`
.. |irow| replace:: `[irow] <[irow.A]>`
.. |icol| replace:: `[icol] <[icol.1]>`
.. |plate| replace:: `[plate] <[plate.NAME]>`
.. |expt| replace:: `[expt]`
"""

from sphinx_rtd_theme import get_html_theme_path
html_theme = "sphinx_rtd_theme"
html_theme_path = [get_html_theme_path()]
html_theme_options = {}

def setup(app):
    app.add_css_file('css/corrections.css')

    app.add_crossref_type(
            'prog',
            'prog',
            objname='command-line program',
            indextemplate='pair: %s; command-line program',
    )
