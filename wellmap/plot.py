#!/usr/bin/env python3

"""\
Visualize the plate layout described by a wellmap TOML file.

Usage:
    wellmap <toml> [<param>...] [-o <path>] [-p] [-c <color>] [-s] [-f]

Arguments:
    <toml>
        TOML file describing the plate layout to display.  For a complete 
        description of the file format, refer to:
        
        https://wellmap.readthedocs.io/en/latest/file_format.html

    <param>
        The name(s) of one or more experimental parameters from the above TOML 
        file to project onto the plate.  For example, if the TOML file contains 
        something equivalent to `well.A1.conc = 1`, then "conc" would be a 
        valid parameter name.

        If no names are given, the default is to display any parameters that 
        have at least two different values.  For complex layouts, this may 
        result in a figure too big to fit on the screen.  The best solution for 
        this (at the moment) is just to specify some parameters to focus on.

Options:
    -o --output PATH
        Output an image of the layout to the given path.  The file type is 
        inferred from the file extension.  If the path contains a dollar sign 
        (e.g. '$.svg'), the dollar sign will be replaced with the base name of 
        the <toml> path.

    -p --print
        Print a paper copy of the layout, e.g. to reference when setting up an 
        experiment.  The default printer for the system will be used.  To see 
        the current default printer, run: `lpstat -d`.  To change the default 
        printer, run: `lpoptions -d <printer name>`.  When printing, the 
        default color scheme is changed to 'dimgray'.  This can still be 
        overridden using the '--color' flag.

    -c --color NAME
        Use the given color scheme to illustrate which wells have which 
        properties.  The given NAME must be one of the color scheme names 
        understood by either `matplotlib` or `colorcet`.  See the links below 
        for the full list of supported colors, but some common choices are 
        given below.  The default is 'rainbow':

        rainbow:  blue, green, yellow, orange, red
        viridis:  purple, green, yellow
        plasma:   purple, red, yellow
        coolwarm: blue, red
        tab10:    blue, orange, green, red, purple, ...
        dimgray:  gray, black

        Matplotlib colors:
        https://matplotlib.org/examples/color/colormaps_reference.html

        Colorcet colors:
        http://colorcet.pyviz.org/

    -s --superimpose
        Superimpose the exact value for each well (i.e. as a word/number) above 
        the layout.  Note that if the values are too big, they might overlap 
        neighboring wells, which could make things hard to read.  If you want 
        more control over the exact formatting of these superimposed values, 
        use the python/R API.

    -f --foreground
        Don't attempt to return the terminal to the user while the GUI runs.  
        This is meant to be used on systems where the program crashes if run in 
        the background.
"""

import wellmap
import colorcet
import numpy as np
import matplotlib.pyplot as plt
import sys, os

from inform import plural
from matplotlib.colors import Normalize
from collections.abc import Mapping
from pathlib import Path
from .util import *

try:
    from typing import Dict, Annotated, get_origin
except ImportError:
    from typing_extensions import Dict, Annotated, get_origin

def main():
    import docopt
    from subprocess import Popen, PIPE

    try:
        args = docopt.docopt(__doc__)
        toml_path = Path(args['<toml>'])
        show_gui = not args['--output'] and not args['--print']

        if show_gui and not args['--foreground']:
            if os.fork() != 0:
                sys.exit()

        style = Style()
        if args['--print']: style.color_scheme = 'dimgray'
        if args['--color']: style.color_scheme = args['--color']
        if args['--superimpose']: style.superimpose_values = True

        fig = show(toml_path, args['<param>'], style=style)

        if args['--output']:
            out_path = args['--output'].replace('$', toml_path.stem)
            fig.savefig(out_path)
            print("Layout written to:", out_path)

        if args['--print']:
            lpr = [
                'lpr',
                '-o', 'ppi=600',
                '-o', 'position=top-left',
                '-o', 'page-top=36',  # 72 pt == 1 in
                '-o', 'page-left=72',
            ]
            p = Popen(lpr, stdin=PIPE)
            fig.savefig(p.stdin, format='png', dpi=600)
            print("Layout sent to printer.")

        if show_gui:
            title = str(toml_path)
            if args['<param>']: title += f' [{", ".join(args["<param>"])}]'
            fig.canvas.setWindowTitle(title)
            plt.show()

    except UsageError as err:
        print(err)
    except LayoutError as err:
        err.toml_path = toml_path
        print(err)

def show(toml_path, params=None, *, style=None):
    """
    Visualize the given microplate layout.

    It's wise to visualize TOML layouts before doing any analysis, to ensure 
    that all of the wells are correctly annotated.  The :prog:`wellmap` 
    command-line program is a useful tool for doing this, but sometimes it's 
    more convenient to make visualizations directly from python (e.g. when 
    working in a jupyter notebook).  That's what this function is for.

    .. note::

        Jupyter will display the layout twice when you use this function, 
        unless you put a semicolon after it.  See :issue:`19` for more 
        information.

    :param str,pathlib.Path toml_path:
        The path to a file describing the layout of one or more plates.  See 
        the :doc:`/file_format` page for details about this file.

    :param str,list params:
        The names of one or more experimental parameters from the above TOML 
        file to visualize.  For example, if the TOML file contains something 
        equivalent to ``well.A1.conc = 1``, then "conc" would be a valid 
        parameter name.  If not specified, the default is to display any 
        parameters that have at least two different values. 

    :param Style style:
        Settings that control miscellaneous aspects of the plot, e.g. colors, 
        dimensions, etc.

    :rtype: matplotlib.figure.Figure
    """
    df, meta = wellmap.load(toml_path, meta=True)
    style = Style.from_merge(style or Style(), meta.style)
    return show_df(df, params, style=style)

def show_df(df, cols=None, *, style=None):
    """
    Visualize the microplate layout described by the given data frame.

    Unlike the `show()` function and the :prog:`wellmap` command-line program, 
    this function is not limited to displaying layouts parsed directly from 
    TOML files.  Any data frame that specifies a well for each row can be 
    plotted.  This provides the means to:

    - Project experimental data onto a layout.
    - Visualize layouts that weren't generated by wellmap in the first place.

    For example, you could load experimental data into a data frame and use 
    this function to visualize it directly, without ever having to specify a 
    layout.  This might be a useful way to get a quick sense for the data.

    :param pandas.DataFrame df:
        The data frame describing the layout to plot.  The data frame must be 
        tidy_: each row must describe a single well, and each column must 
        describe a single aspect of each well.  The location of each well must 
        be specified using one or more of the same columns that wellmap uses 
        for that purpose, namely:

        - *plate*
        - *well*
        - *well0*
        - *row*
        - *col*
        - *row_i*
        - *col_j*

        See `load()` for the exact meanings of these columns.  It's not 
        necessary to specify all of these columns, there just needs to be 
        enough information to locate each well.  If the *plate* column is 
        missing, it is assumed that all of the wells are on the same plate.  It 
        is also assumed that any redundant columns (e.g. *row* and *row_i*) 
        will be consistent with each other.

        Any scalar-valued columns other than these can be plotted.

    :param str,list cols:
        Which columns to plot onto the layout.  The columns used to locate the 
        wells (listed above) cannot be plotted.  The default is to include any 
        columns that have at least two different values.

    :param Style style:
        Settings than control miscellaneous aspects of the plot, e.g. colors, 
        dimensions, etc.

    :rtype: matplotlib.figure.Figure
    """

    # The whole architecture of this function is dictated by (what I consider 
    # to be) a small and obscure bug in matplotlib.  That bug is: if you are 
    # displaying a figure in the GUI and you use `set_size_inches()`, the whole 
    # GUI will have the given height, but the figure itself will be too short 
    # by the height of the GUI control panel.  That control panel has different 
    # heights with different backends (and no way that I know of to query what 
    # its height will be), so `set_size_inches()` is not reliable.
    #
    # The only way to reliably control the height of the figure is to provide a 
    # size when constructing it.  But that requires knowing the size of the 
    # figure in advance.  I would've preferred to set the size at the end, 
    # because by then I know everything that will be in the figure.  Instead, I 
    # have to basically work out some things twice (once to figure out how big 
    # they will be, then a second time to actually put them in the figure).
    #
    # In particular, I have to work out the colorbar labels twice.  These are 
    # the most complicated part of the figure layout, because they come from 
    # the TOML file and could be either very narrow or very wide.  So I need to 
    # do a first pass where I plot all the labels on a dummy figure, get their 
    # widths, then allocate enough room for them in the main figure.  
    # 
    # I also need to work out the dimensions of the plates twice, but that's a 
    # simpler calculation.

    style = style or Style()

    df = require_well_locations(df)
    plates = sorted(df['plate'].unique())
    params = pick_params(df, cols)

    fig, axes, dims = setup_axes(df, plates, params, style)

    try:
        for i, param in enumerate(params):
            cmap = get_colormap(style[param].color_scheme)
            colors = setup_color_bar(axes[i,-1], df, param, cmap)

            for j, plate in enumerate(plates):
                plot_plate(axes[i,j], df, plate, param, style, dims, colors)

        for i, param in enumerate(params):
            axes[i,0].set_ylabel(param)
        for j, plate in enumerate(plates):
            axes[0,j].set_xlabel(plate)
            axes[0,j].xaxis.set_label_position('top')

        for ax in axes[1:,:-1].flat:
            ax.set_xticklabels([])
        for ax in axes[:,1:-1].flat:
            ax.set_yticklabels([])

    except:
        plt.close(fig)
        raise

    return fig

def plot_plate(ax, df, plate, param, style, dims, colors):
    # Fill in a matrix with integers representing each value of the given 
    # experimental parameter.
    matrix = np.full(dims.shape, np.nan)
    q = df.query('plate == @plate')

    for _, well in q.iterrows():
        i = well['row_i'] - dims.i0
        j = well['col_j'] - dims.j0
        matrix[i, j] = x = colors.transform(well[param])

        if style[param].superimpose_values:
            bg = colors.cmap(colors.norm(x))
            fg = choose_foreground_color(bg)

            text = format(well[param], style[param].superimpose_format)
            kwargs = {
                    'color': fg,
                    'horizontalalignment': 'center',
                    'verticalalignment': 'center_baseline',
                    **style[param].superimpose_kwargs,
            }
            ax.text(j, i, text, **kwargs)

    ax.imshow(
            matrix,
            norm=colors.norm,
            cmap=colors.cmap,
            origin='upper',
            interpolation='nearest',
    )

    ax.set_xticks(dims.xticks)
    ax.set_yticks(dims.yticks)
    ax.set_xticks(dims.xticksminor, minor=True)
    ax.set_yticks(dims.yticksminor, minor=True)
    ax.set_xticklabels(dims.xticklabels)
    ax.set_yticklabels(dims.yticklabels)
    ax.grid(which='minor')
    ax.tick_params(which='both', axis='both', length=0)
    ax.xaxis.tick_top()

def pick_params(df, user_params):
    if isinstance(user_params, str):
        user_params = [user_params]

    wellmap_cols = ['plate', 'well', 'well0', 'row', 'col', 'row_i', 'col_j', 'path']
    user_cols = [x for x in df.columns if x not in wellmap_cols]

    if user_params:
        # Complain if the user specified any columns that don't exist.

        # Using lists (slower) instead of sets (faster) to maintain the order 
        # of the columns in case we want to print an error message.
        unknown_params = [
                x for x in user_params
                if x not in user_cols
        ]
        if unknown_params:
            raise UsageError(f"No such {plural(unknown_params):parameter/s}: {quoted_join(unknown_params)}\nDid you mean: {quoted_join(user_cols)}")

        return user_params

    # If the user didn't specify any columns, show any that have more than one 
    # unique value.
    else:
        degenerate_cols = [
                x for x in user_cols
                if df[x].nunique() == 1
        ]
        non_degenerate_cols = [
                x for x in user_cols
                if x not in degenerate_cols
        ]
        if not non_degenerate_cols:
            if degenerate_cols:
                raise UsageError(f"Found only degenerate parameters (i.e. with the same value in every well): {quoted_join(degenerate_cols)}")
            else:
                raise LayoutError("No experimental parameters found.")

        return non_degenerate_cols

def setup_axes(df, plates, params, style):
    from mpl_toolkits.axes_grid1 import Divider
    from mpl_toolkits.axes_grid1.axes_size import Fixed

    # These assumptions let us simplify some code, and should always be true.
    assert len(plates) > 0
    assert len(params) > 0

    # Determine how much data will be shown in the figure:
    num_plates = len(plates)
    num_params = len(params)
    dims = Dimensions(df)

    bar_label_width = guess_param_label_width(df, params)

    # Define the grid on which the axes will live:
    h_divs  = [
            style.left_margin,
    ]
    for _ in plates:
        h_divs += [
                style.cell_size * dims.num_cols,
                style.pad_width,
        ]
    h_divs[-1:] = [
            style.bar_pad_width,
            style.bar_width,
            style.right_margin + bar_label_width,
    ]

    v_divs = [
            style.top_margin,
    ]
    for param in params:
        v_divs += [
                max(
                    style.cell_size * dims.num_rows,
                    style.bar_width * dims.num_values[param],
                ),
                style.pad_height,
        ]
    v_divs[-1:] = [
            style.bottom_margin,
    ]

    # Add up all the divisions to get the width and height of the figure:
    figsize = sum(h_divs), sum(v_divs)

    # Make the figure:
    fig, axes = plt.subplots(
            num_params,
            num_plates + 1,  # +1 for the colorbar axes.
            figsize=figsize,
            squeeze=False,
    )

    # Position the axes:
    rect = 0.0, 0.0, 1, 1
    h_divs = [Fixed(x) for x in h_divs]
    v_divs = [Fixed(x) for x in reversed(v_divs)]
    divider = Divider(fig, rect, h_divs, v_divs, aspect=False)

    for i in range(num_params):
        for j in range(num_plates + 1):
            loc = divider.new_locator(nx=2*j+1, ny=2*(num_params - i) - 1)
            axes[i,j].set_axes_locator(loc)

    return fig, axes, dims

def setup_color_bar(ax, df, param, cmap):
    from matplotlib.colorbar import ColorbarBase

    colors = Colors(cmap, df, param)

    bar = ColorbarBase(
            ax,
            norm=colors.norm,
            cmap=colors.cmap,
            boundaries=colors.boundaries,
    )
    bar.set_ticks(colors.ticks)
    bar.set_ticklabels(colors.ticklabels)

    ax.invert_yaxis()

    return colors

def guess_param_label_width(df, params):
    # I've seen some posts suggesting that this might not work on Macs.  I 
    # can't test that, but if this ends up being a problem, I probably need to 
    # wrap this is a try/except block and fall back to guessing a width based 
    # on the number of characters in the string representation of each label.
    #
    # https://stackoverflow.com/questions/22667224/get-text-bounding-box-independent-of-backend

    width = 0
    fig, ax = plt.subplots()

    for param in params:
        labels = df[param].unique()
        ax.set_yticks(range(len(labels)))
        ax.set_yticklabels(labels)

        width = max(width, get_yticklabel_width(ax))

    plt.close(fig)
    return width

def choose_foreground_color(bg_color):
    # Decide whether to use white or black text, based on the background color.  
    # The basic algorithm is to scale the primaries by their perceived 
    # brightness, then to compare to a threshold value that generally works 
    # well for monitors.
    #
    # https://stackoverflow.com/questions/3942878/how-to-decide-font-color-in-white-or-black-depending-on-background-color

    r, g, b = bg_color[:3]
    grey = r * 0.299 + g * 0.587 + b * 0.114
    return 'black' if grey > 0.588 else 'white'

def get_colormap(name):
    try:
        return colorcet.cm[name]
    except KeyError:
        return plt.get_cmap(name)

def get_yticklabel_width(ax):
    # With some backends, getting the renderer like this may trigger a warning 
    # and cause matplotlib to drop down to the Agg backend.
    fig = ax.get_figure()
    renderer = fig.canvas.get_renderer()
    width = max(
            artist.get_window_extent(renderer).width
            for artist in ax.get_yticklabels()
    )
    dpi = fig.get_dpi()
    return width / dpi

_by_param = object()

def _find_param_level_attrs(cls):
    cls._param_level_attrs = []

    for name, annot in cls.__annotations__.items():
        if get_origin(annot) is Annotated and _by_param in annot.__metadata__:
            cls._param_level_attrs.append(name)

    return cls

def _find_mutable_defaults(cls):
    cls._default_factories = {}

    for name, annotation in cls.__annotations__.items():
        if get_origin(annotation) is Annotated:
            annotation = annotation.__origin__

        if annotation in [list, dict]:
            cls._default_factories[name] = annotation

    return cls

def _fix_init_signature(cls):
    from inspect import Signature, Parameter

    # This is just for the benefit of code editing/documentation tools.  
    # Changing the signature like this doesn't affect how the constructor 
    # behaves.

    init_params = [
            Parameter('self', kind=Parameter.POSITIONAL_OR_KEYWORD),
    ]

    for name, annotation in cls.__annotations__.items():
        try:
            default_factory = cls._default_factories[name]
        except KeyError:
            default = getattr(cls, name)
        else:
            default = default_factory()

        if get_origin(annotation) is Annotated:
            annotation = annotation.__origin__

        param = Parameter(
                name=name,
                kind=Parameter.KEYWORD_ONLY,
                default=default,
                annotation=annotation,
        )
        init_params.append(param)

    param = Parameter(
            name='by_param',
            kind=Parameter.KEYWORD_ONLY,
            default={},
            annotation=Dict[str, dict],
    )
    init_params.append(param)

    cls.__init__.__signature__ = Signature(init_params)
    return cls

@_fix_init_signature
@_find_param_level_attrs
@_find_mutable_defaults
class Style:
    """
    Describe how to plot well layouts.

    Style objects exist to be passed to `show()` or `show_df()`, where they 
    determine various aspects of the plots' appearances.  You can create/modify 
    style objects yourself (see examples below), or you can load them from TOML 
    files via the ``meta=True`` argument to `load`.

    Examples:
    
        Specify a color scheme (via constructor)::

            >>> Style(color_scheme='coolwarm')

        Specify a color scheme (via attribute)::
            
            >>> style = Style()
            >>> style.color_scheme = 'coolwarm'

        Specify a color scheme for only a specific parameter (via constructor)::

            >>> Style(by_param={'param': {'color_scheme': 'coolwarm'}})

        Specify a color scheme for only a specific parameter (via attribute)::

            >>> style = Style()
            >>> style['param'].color_scheme = 'coolwarm'
    """

    # This class is pretty complicated, because it has to achieve all of the 
    # following:
    #
    # - User-facing API: This class is meant to be used directly by end users, 
    #   so it needs a nice API.  My goal was to make it feel like a data class, 
    #   e.g. a constructor with a correct signature, a meaningful `repr()`, 
    #   attribute-style accessors, etc.
    #
    # - Merging: There are multiple places where we need to merge one style 
    #   into another, e.g. when one layout with a style includes another layout 
    #   with a style.  Doing this requires keeping track of what values were 
    #   actually specified by the user, as opposed to having default values.  
    #
    # - Error checking: We don't want to silently do nothing if the user 
    #   specifies a style option that doesn't exist (e.g. due to a 
    #   misspelling).  So this class needs to be aware of what options actually 
    #   exist, and raise an error whenever an unknown option is encountered.
    #
    # - Parameter-level options: Some style options can have different values 
    #   for each parameter in a layout, e.g. `color_scheme` and 
    #   `superimpose_values`.

    cell_size: float = 0.25
    """
    The size of the boxes representing each well, in inches.
    """

    pad_width: float = 0.20
    """
    The vertical padding between layouts, in inches.
    """

    pad_height: float = 0.20
    """
    The horizontal padding between layouts, in inches.
    """

    bar_width: float = 0.15
    """
    The width of the color bar, in inches.
    """

    bar_pad_width: float = pad_width
    """
    The horizontal padding between the color bar and the nearest layout, in 
    inches.
    """

    top_margin: float = 0.5
    """
    The space between the layouts and the top edge of the figure, in inches.
    """

    left_margin: float = 0.5
    """
    The space between the layouts and the left edge of the figure, in inches.
    """

    right_margin: float = pad_width
    """
    The space between the layouts and the right edge of the figure, in inches.
    """

    bottom_margin: float = pad_height
    """
    The space between the layouts and the bottom edge of the figure, in inches.
    """

    color_scheme: Annotated[str, _by_param] = 'rainbow'
    """
    The name of the color scheme to use.  Each different value for each 
    different parameter will be assigned a color from this scheme.  Any 
    name understood by either colorcet_ or matplotlib_ can be used.

    .. _matplotlib: https://matplotlib.org/examples/color/colormaps_reference.html
    .. _colorcet: http://colorcet.pyviz.org/
    """

    superimpose_values: Annotated[bool, _by_param] = False
    """
    Whether or not to write exact values (i.e. as words/numbers) above each 
    well in the layout.  Use True/False to enable/disable this behavior for all 
    parameters, or use a container (e.g. list, set) to enable it only for 
    specific parameter names.
    """

    superimpose_format: Annotated[str, _by_param] = ''
    """
    The `format string 
    <https://docs.python.org/3/library/string.html#formatspec>`_ to use when 
    superimposing values over each well, e.g. 
    """

    superimpose_kwargs: Annotated[dict, _by_param] = None
    """
    Any keyword arguments to pass on to `matplotlib.text.Text` when rendering 
    the superimposed values over each well.
    """

    def __init__(self, **kwargs):
        self._style = {}
        self._param_styles = {}
        self._mutable_defaults = {}

        # Assign each attribute one at a time, to reuse the same error-checking 
        # logic that gets applied normally.

        by_param = kwargs.pop('by_param', {})

        for name, value in kwargs.items():
            setattr(self, name, value)

        for param, style in by_param.items():
            if not isinstance(style, Mapping):
                raise ValueError(f"expected *by_param* to be a dict of dicts, got: {by_param!r}")
            for name, value in style.items():
                setattr(self[param], name, value)

    def __eq__(self, other):

        # Make sure that default values are handled correctly by actually
        # looking up each attribute through the normal channels.

        def get_all_attrs(style, params):
            base = {
                    k: getattr(style, k)
                    for k in style.__class__.__annotations__
            }
            by_param = {
                    k1: {
                        k2: getattr(style[k1], k2)
                        for k2 in self._param_level_attrs
                    }
                    for k1 in params
            }
            return base, by_param

        params = set(self._param_styles) | set(other._param_styles)

        return (
                self.__class__ is other.__class__ and
                get_all_attrs(self, params) == get_all_attrs(other, params)
        )

    def __repr__(self):
        kwargs = []
        order = {
                name: i
                for i, name in enumerate(self.__class__.__annotations__)
        }

        mutable_defaults = {
                k: v
                for k, v in self._mutable_defaults.items()
                if v
        }
        non_default_styles = {**mutable_defaults, **self._style}

        for name in sorted(non_default_styles, key=lambda x: order[x]):
            kwargs.append(f'{name}={non_default_styles[name]!r}')

        if self._param_styles:
            kwargs.append(f'by_param={self._param_styles!r}')

        return f'{self.__class__.__name__}({", ".join(kwargs)})'

    def __getattribute__(self, name):
        cls = super().__getattribute__('__class__')

        # We need `__getattribute__()` instead of `__getattr__()` because there 
        # are class-level attributes with the same names as the instance-level 
        # attributes that we want to generate dynamically.

        if name in cls.__annotations__:
            try:
                return self._style[name]
            except KeyError:
                pass

            if name in cls._default_factories:
                try:
                    return self._mutable_defaults[name]
                except KeyError:
                    default = cls._default_factories[name]()
                    self._mutable_defaults[name] = default
                    return default

            return getattr(self.__class__, name)

        else:
            return super().__getattribute__(name)

    def __getattr__(self, name):
        known_names = self.__class__.__annotations__
        raise StyleAttributeError(name, known_names)

    def __setattr__(self, name, value):
        known_names = self.__class__.__annotations__

        if name.startswith('_'):
            super().__setattr__(name, value)
        elif name in known_names:
            self._style[name] = value
            self._mutable_defaults.pop(name, None)
        else:
            raise StyleAttributeError(name, known_names)

    def __getitem__(self, param):
        """
        Get the style for a specific parameter.

        The following style options can be specified on a per-parameter basis:

        - `color_scheme`
        - `superimpose_values`
        - `superimpose_format`
        - `superimpose_kwargs`

        This method will return an object that allows getting an setting 
        options specific to the given parameter.  Specifically, the object will 
        have an attribute corresponding to each of the above options.  If no 
        parameter-specific value has been specified for an option, its value 
        will default to that in the parent `Style` object.
        """
        return Style._ParamStyle(self, param)

    def merge(self, other):
        """
        Merge the options from another style object into this one.

        If both styles specify the same option, for value from this style will 
        be used (i.e. the value won't change).  The `superimpose_kwargs` option 
        (which is a dictionary) is merged recursively in this same manner.
        """
        recursive_merge(self._style, other._style)
        recursive_merge(self._param_styles, other._param_styles)
        recursive_merge(self._mutable_defaults, other._mutable_defaults)

        for key in set(self._style) & set(self._mutable_defaults):
            recursive_merge(self._style[key], self._mutable_defaults[key])
            del self._mutable_defaults[key]

    @classmethod
    def from_merge(cls, *others):
        """
        Combine all of the given styles into a single object.

        If multiple styles specify the same option, the earlier value will be 
        used.  The `merge` for more details.
        """
        style = cls()
        for other in others:
            style.merge(other)
        return style

    class _ParamStyle:

        def __init__(self, style, param):
            self._style = style
            self._param = param

        def __repr__(self):
            return f'{self._style}[{self._param!r}]'

        def __getattr__(self, name):
            if name in self._style._param_level_attrs:
                try:
                    return self._style._param_styles[self._param][name]
                except KeyError:
                    return getattr(self._style, name)

            else:
                raise StyleAttributeError(
                        name,
                        self._style._param_level_attrs,
                        is_param_level=True,
                )

        def __setattr__(self, name, value):
            if name.startswith('_'):
                super().__setattr__(name, value)
            elif name in self._style._param_level_attrs:
                self._style._param_styles.setdefault(self._param, {})[name] = value
            else:
                raise StyleAttributeError(
                        name,
                        self._style._param_level_attrs,
                        is_param_level=True,
                )


class Dimensions:

    def __init__(self, df):
        self.i0 = df['row_i'].min()
        self.j0 = df['col_j'].min() 
        self.num_rows = df['row_i'].max() - self.i0 + 1
        self.num_cols = df['col_j'].max() - self.j0 + 1
        self.num_values = df.nunique()
        self.shape = self.num_rows, self.num_cols

        self.xticks = np.arange(self.num_cols)
        self.yticks = np.arange(self.num_rows)

        self.xticksminor = np.arange(self.num_cols + 1) - 0.5
        self.yticksminor = np.arange(self.num_rows + 1) - 0.5

        self.xticklabels = [
                wellmap.col_from_j(j + self.j0)
                for j in self.xticks
        ]
        self.yticklabels = [
                wellmap.row_from_i(i + self.i0)
                for i in self.yticks
        ]

class Colors:

    def __init__(self, cmap, df, param):
        cols = ['plate', 'row_i', 'col_j']
        rows = df[param].notna()
        labels = df[rows]\
                .sort_values(cols)\
                .groupby(param, sort=False)\
                .head(1)

        self.map = {x: i for i, x in enumerate(labels[param])}

        n = len(self.map)
        self.cmap = cmap
        self.norm = Normalize(vmin=0, vmax=max(n-1, 1))
        self.boundaries = np.arange(n+1) - 0.5
        self.ticks = np.fromiter(self.map.values(), dtype=int, count=n)
        self.ticklabels = list(self.map.keys())

    def transform(self, x):
        def is_nan(x):
            return isinstance(x, float) and np.isnan(x)
        return self.map[x] if not is_nan(x) else np.nan


class UsageError(Exception):
    pass
