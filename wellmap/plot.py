#!/usr/bin/env python3

"""\
Visualize the plate layout described by a wellmap TOML file.

Usage:
    wellmap <toml> [<attr>...] [-o <path>] [-p] [-c <color>] [-f]

Arguments:
    <toml>
        TOML file describing the plate layout to display.  For a complete 
        description of the file format, refer to:
        
        https://wellmap.readthedocs.io/en/latest/file_format.html

    <attr>
        The name(s) of one or more attributes from the above TOML file to 
        project onto the plate.  For example, if the TOML file contains 
        something equivalent to `well.A1.conc = 1`, then "conc" would be a 
        valid attribute.

        If no attributes are specified, the default is to display any 
        attributes that have at least two different values.  For complex 
        layouts, this may result in a figure too big to fit on the screen.
        The best solution for this is just to specify a smaller number of 
        attributes to focus on.

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

    -f --foreground
        Don't attempt to return the terminal to the user while the GUI runs.  
        This is meant to be used on systems where the program crashes if run in 
        the background.
"""

import wellmap
import colorcet
import numpy as np
import matplotlib.pyplot as plt
import sys, os, shlex

from wellmap import ConfigError
from inform import plural
from matplotlib.colors import BoundaryNorm, Normalize
from pathlib import Path
from .util import *

CELL_SIZE = 0.25
PAD_WIDTH = 0.20
PAD_HEIGHT = 0.20
BAR_WIDTH = 0.15
BAR_PAD_WIDTH = PAD_WIDTH
TOP_MARGIN = 0.5
LEFT_MARGIN = 0.5
RIGHT_MARGIN = PAD_WIDTH
BOTTOM_MARGIN = PAD_HEIGHT

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

        default_color = 'dimgray' if args['--print'] else 'rainbow'
        color = args['--color'] or default_color

        fig = show(toml_path, args['<attr>'], color)

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
            if args['<attr>']: title += f' [{", ".join(args["<attr>"])}]'
            fig.canvas.set_window_title(title)
            plt.show()

    except CliError as err:
        print(err)
    except ConfigError as err:
        err.toml_path = toml_path
        print(err)

def show(toml_path, attrs=None, color='rainbow'):
    """
    Visualize the given microplate layout.

    It's wise to visualize TOML layouts before doing any analysis, to ensure 
    that all of the wells are correctly annotated.  The :prog:`wellmap` 
    command-line program is a useful tool for doing this, but sometimes it's 
    more convenient to make visualizations directly from python (e.g. when 
    working in a jupyter notebook).  That's what this function is for.

    :param str,pathlib.Path toml_path:
        The path to a file describing the layout of one or more plates.  See 
        the :doc:`/file_format` page for details about this file.

    :param list attrs:
        A list of attributes from the above TOML file to visualize.  For 
        example, if the TOML file contains something equivalent to 
        ``well.A1.conc = 1``, then "conc" would be a valid attribute.  If no 
        attributes are specified, the default is to display any attributes that 
        have at least two different values. 

    :param str color:
        The name of the color scheme to use.  Each different value for each 
        different attribute will be assigned a color from this scheme.  Any 
        name understood by either colorcet_ or matplotlib_ can be used.

    :rtype: matplotlib.figure.Figure

    .. _matplotlib: https://matplotlib.org/examples/color/colormaps_reference.html
    .. _colorcet: http://colorcet.pyviz.org/
    """
    df = wellmap.load(toml_path)
    cmap = get_colormap(color)
    return plot_layout(df, attrs, cmap=cmap)


def plot_layout(df, user_attrs, cmap):
    import matplotlib.pyplot as plt

    # The whole architecture of this program is dictated by a small and obscure 
    # bug in matplotlib.  (Well, I think it's a bug.)  That bug is: if you are 
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

    if 'plate' not in df:
        df.insert(0, 'plate', '')

    plates = sorted(df['plate'].unique())
    attrs = pick_attrs(df, user_attrs)

    fig, axes, dims = setup_axes(df, plates, attrs)

    for i, attr in enumerate(attrs):
        colors = pick_colors(axes[i,-1], df, attr, cmap)

        for j, plate in enumerate(plates):
            plot_plate(axes[i,j], df, plate, attr, dims, colors)

    for i, attr in enumerate(attrs):
        axes[i,0].set_ylabel(attr)
    for j, plate in enumerate(plates):
        axes[0,j].set_xlabel(plate)
        axes[0,j].xaxis.set_label_position('top')

    for ax in axes[1:,:-1].flat:
        ax.set_xticklabels([])
    for ax in axes[:,1:-1].flat:
        ax.set_yticklabels([])

    return fig

def plot_plate(ax, df, plate, attr, dims, colors):
    # Fill in a matrix with integers representing each value of the given 
    # attribute.
    matrix = np.full(dims.shape, np.nan)
    q = df.query('plate == @plate')

    for _, well in q.iterrows():
        i = well['row_i'] - dims.i0
        j = well['col_j'] - dims.j0
        matrix[i, j] = colors.transform(well[attr])

    # Plot a heatmap.
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

def pick_attrs(df, user_attrs):
    wellmap_cols = ['plate', 'well', 'well0', 'row', 'col', 'row_i', 'col_j', 'path']
    user_cols = [x for x in df.columns if x not in wellmap_cols]

    if user_attrs:
        # Complain if the user specified any columns that don't exist.

        # Using lists (slower) instead of sets (faster) to maintain the order 
        # of the attributes in case we want to print an error message.
        unknown_attrs = [
                x for x in user_attrs
                if x not in user_cols
        ]
        if unknown_attrs:
            raise ConfigError(f"No such {plural(unknown_attrs):attribute/s}: {quoted_join(unknown_attrs)}.\nDid you mean: {quoted_join(user_cols)}")

        return user_attrs

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
                raise CliError(f"Found only degenerate attributes (i.e. with the same value in every well): {quoted_join(degenerate_cols)}")
            else:
                raise ConfigError(f"No attributes defined.")

        return non_degenerate_cols

def pick_colors(ax, df, attr, cmap):
    from matplotlib.colorbar import ColorbarBase

    colors = Colors(cmap, df[attr])

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

def setup_axes(df, plates, attrs):
    from mpl_toolkits.axes_grid1 import Divider
    from mpl_toolkits.axes_grid1.axes_size import Fixed

    # These assumptions let us simplify some code, and should always be true.
    assert len(plates) > 0
    assert len(attrs) > 0

    # Determine how much data will be shown in the figure:
    num_plates = len(plates)
    num_attrs = len(attrs)
    dims = Dimensions(df)

    bar_label_width = guess_attr_label_width(df, attrs)

    # Define the grid on which the axes will live:
    h_divs  = [
            LEFT_MARGIN,
    ]
    for _ in plates:
        h_divs += [
                CELL_SIZE * dims.num_cols,
                PAD_WIDTH,
        ]
    h_divs[-1:] = [
            BAR_PAD_WIDTH,
            BAR_WIDTH,
            RIGHT_MARGIN + bar_label_width,
    ]

    v_divs = [
            TOP_MARGIN,
    ]
    for attr in attrs:
        v_divs += [
                max(
                    CELL_SIZE * dims.num_rows,
                    BAR_WIDTH * dims.num_values[attr],
                ),
                PAD_HEIGHT,
        ]
    v_divs[-1:] = [
            BOTTOM_MARGIN,
    ]

    # Add up all the divisions to get the width and height of the figure:
    figsize = sum(h_divs), sum(v_divs)

    # Make the figure:
    fig, axes = plt.subplots(
            num_attrs,
            num_plates + 1,  # +1 for the colorbar axes.
            figsize=figsize,
            squeeze=False,
    )

    # Position the axes:
    rect = 0.0, 0.0, 1, 1
    h_divs = [Fixed(x) for x in h_divs]
    v_divs = [Fixed(x) for x in reversed(v_divs)]
    divider = Divider(fig, rect, h_divs, v_divs, aspect=False)

    for i in range(num_attrs):
        for j in range(num_plates + 1):
            loc = divider.new_locator(nx=2*j+1, ny=2*(num_attrs - i) - 1)
            axes[i,j].set_axes_locator(loc)

    return fig, axes, dims

def guess_attr_label_width(df, attrs):
    # I've seen some posts suggesting that this might not work on Macs.  I 
    # can't test that, but if this ends up being a problem, I probably need to 
    # wrap this is a try/except block and fall back to guessing a width based 
    # on the number of characters in the string representation of each label.

    width = 0
    fig, ax = plt.subplots()

    for attr in attrs:
        labels = df[attr].unique()
        ax.set_yticks(range(len(labels)))
        ax.set_yticklabels(labels)

        width = max(width, get_yticklabel_width(fig, ax))

    plt.close(fig)
    return width

def get_colormap(name):
    try:
        return colorcet.cm[name]
    except KeyError:
        return plt.get_cmap(name)

def get_yticklabel_width(fig, ax):
    # With some backends, getting the renderer like this may trigger a warning 
    # and cause matplotlib to drop down to the Agg backend.
    from matplotlib import tight_layout
    renderer = tight_layout.get_renderer(fig)

    width = max(
            artist.get_window_extent(renderer).width
            for artist in ax.get_yticklabels()
    )
    dpi = ax.get_figure().get_dpi()

    return width / dpi

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

    def __init__(self, cmap, values):
        values = values.dropna().unique()

        # If we don't sort, the values will be listing in the order they appear 
        # in the TOML file.  This is a reasonable default, but it can break 
        # down when there are included or concatenated files.
        # 
        # For numbers and dates, the natural ordering (least to greatest) is 
        # likely to be useful, so explicitly sorting the values makes the 
        # display more robust and is worth doing.  
        #
        # For strings, the natural ordering (alphabetical) is not likely to be 
        # useful, so instead we keep the values in their order-of-appearance.  
        # This might break down in the more-complicated cases mentioned above, 
        # but in the common case its the most likely to be useful.
        #
        # (Note that the only scalar types in the TOML format are: string, int, 
        # float, bool, and datetime.  Of these, string is the only one that 
        # doesn't have a meaningful natural ordering.)

        if not any(isinstance(x, str) for x in values):
            # If sorting fails (e.g. due to mixed types), just fall back on the 
            # original ordering.
            try: values = sorted(values)
            except ValueError: pass

        self.map = {x: i for i, x in enumerate(values)}

        n = len(self.map)
        self.cmap = cmap
        self.norm = Normalize(vmin=0, vmax=max(n-1, 1))
        self.boundaries = np.arange(n+1) - 0.5
        self.ticks = np.fromiter(self.map.values(), dtype=int, count=n)
        self.ticklabels = list(self.map.keys())

    def transform(self, x):
        return self.map[x] if not self.isnan(x) else np.nan

    @staticmethod
    def isnan(x):
        return isinstance(x, float) and np.isnan(x)

class CliError(Exception):
    pass
