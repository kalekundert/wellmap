#!/usr/bin/env python3

import sys, re, itertools, inspect
import pandas as pd

from pathlib import Path
from dataclasses import dataclass
from inform import plural
from copy import deepcopy
from warnings import warn
from typing import Dict, Set, Any
from .plot import Style
from .util import *

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

# Data Structures
# ===============
# `config`
#   A direct reflection of the TOML input file, with all the [meta] fields 
#   resolved.  Arbitrary parameters can be specified on a per-experiment, 
#   per-plate, per-row, per-column, or per-well basis.  
#
# `wells`
#   Dictionary where the keys are (row, col) well indices and the values are 
#   dictionaries containing arbitrary information about said well.  This is 
#   basically a version of the `config` data structure where all the messy well 
#   names have been resolved to simple indices, and all the parameters have 
#   been resolved on a per-well basis.
#
# `table`
#   A pandas DataFrame derived from the `wells` data structure.  Each row 
#   represents a well, and each column represents one of the fields in the well 
#   dictionaries.  Columns identifying the plate and well are also added.

def load(
        toml_path,
        *,
        data_loader=None,
        merge_cols=None,
        path_guess=None, 
        path_required=False,
        on_alert=None,
        meta=False,
        extras=False,
        report_dependencies=False, 
):
    """
    Load a microplate layout from a TOML file.

    Parse the given TOML file and return a `pandas.DataFrame` with a row for 
    each well and a column for each experimental condition specified in that 
    file.  If the **data_loader** and **merge_cols** arguments are provided 
    (which is the most typical use-case), that data frame will also contain 
    columns for any data associated with each well.

    :param str,pathlib.Path toml_path:
        The path to a file describing the layout of one or more plates.  See 
        the :doc:`/file_format` page for details about this file.

    :param callable data_loader:
        Indicates that `load()` should attempt to load the actual data 
        associated with the plate layout, in addition to loading the layout 
        itself.  The argument should be a function that takes a `pathlib.Path` 
        to a data file, parses it, and returns a `pandas.DataFrame` containing 
        the parsed data.  The function may also take an argument named 
        "extras", in which case the **extras** return value (described below) 
        will be provided.  Note that specifying a data loader implies that 
        **path_required** is True.

    :param bool,dict merge_cols:
        Indicates whether or not---and if so, how---`load()` should merge the 
        data frames representing the plate layout and the actual data (provided 
        by **data_loader**).  The argument can either be a boolean or a 
        dictionary:

        If *False* (or falsey, e.g. ``None``, ``{}``, etc.), the data frames 
        will be returned separately and not be merged.  This is the default 
        behavior.

        If *True*, the data frames will be merged using any columns that 
        share the same name.  For example, the layout will always have a 
        column named *well*, so if the actual data also has a column named 
        *well*, the merge would happen on those columns.

        If a dictionary, the data frames will be merged using the columns 
        identified in each key-value pair of the dictionary.  The keys should 
        be column names from the data frame representing the plate layout 
        (described below; see the **layout** return value), and the values 
        should be column names from the data frame returned by 
        **data_loader**.  Below are some examples of this argument:

        - :code:`{'well0': 'Well'}`: Indicates that the "Well" column in the 
          data contains zero-padded well names, like "A01", "A02", etc.

        - :code:`{'row_i': 'Row', 'col_j': 'Col'}`: Indicates that the 'Row' 
          and 'Col' columns in the data contain 0-indexed coordinates (e.g. 0, 
          1, 2, ...) identifying each row and column, respectively.

        Some details and caveats:

        - In order to successfully merge two columns, the values in those 
          columns must correspond exactly.  For example, a column that contains 
          unpadded well names like "A1" cannot be merged with a column that 
          contains padded well names like "A01".  This is why the **layout** 
          data frame contains so many redundant columns: to increase the chance 
          that one will correspond exactly with a column provided by the data.  
          In some cases, though, it may be necessary for the **data_loader** 
          function to construct an appropriate merge column.

        - The data frame returned by **data_loader()** must be tidy_.  Briefly, 
          a data frame is tidy if each of its columns represents a single 
          variable (e.g. time, fluorescence) and each of its rows represents a 
          single observation.

        - The *path* column of the layout is automatically included in the 
          merge and never has to be specified (although it is not an error to 
          do so).  The reason for this special-case is that `load()` itself 
          knows what path each data frame was loaded from.
       
    :param str path_guess:
        Where to look for a data file if none is specified in the given TOML 
        file.  In other words, this is the default value for `meta.path`.  This 
        path is interpreted relative to the TOML file itself (unless it's an 
        absolute path) and is formatted with a `pathlib.Path` representing said 
        TOML file.  In code, that would be: 
        ``path_guess.format(Path(toml_path))``.  A typical value would be 
        something like ``'{0.stem}.csv'``.

    :param bool path_required:
        Indicates whether or not the given TOML file must reference one or more 
        data files.  A `ValueError` will be raised if this condition is not 
        met.  Data files found via **path_guess** are acceptable for this 
        purpose.

    :param bool meta:
        If true, return a :class:`~wellmap.Meta` object containing miscellaneous 
        information that was read from the TOML file but not part of the 
        layout.  This includes (i) a dictionary with all the key/values pairs 
        present in the TOML file but not part of the layout, (ii) a set of all 
        the TOML files that were read in the process of loading the layout from 
        the given **toml_path**, (iii) and a `Style` object describing how to 
        plot the layout itself.

    :param bool extras:
        `Deprecated <load-extras-deps>`.

    :param bool report_dependencies:
        `Deprecated <load-extras-deps>`.

    :param callable on_alert:
        A callback to invoke if the given TOML file contains a warning for the 
        user.  The default behavior is to print the warning to the terminal via
        stderr.  If a callback is provided, it must take two arguments: a 
        `pathlib.Path` to the TOML file containing the alert, and the message 
        itself.  Note that this could be called more than once, e.g. if there 
        are included or concatenated files.

    :returns:
        If neither **data_loader** nor **merge_cols** were provided:
 
        - **layout** (`pandas.DataFrame`) – Information about the plate layout 
          parsed from the given TOML file.  The data frame will have a row for 
          each well and a column for each experimental condition.  In addition, 
          there will be several columns identifying each well:
 
          - *plate*: The name of the plate for this well.  This column will 
            not be present if there are no ``[plate]`` blocks in the TOML file.
          - *path*: The path to the data file associated with the plate for 
            this well.  This column will not be present if no data files were 
            referenced by the TOML file.
          - *well*: The name of the well, e.g. "A1".
          - *well0*: The zero-padded name of the well, e.g. "A01".
          - *row*: The name of the row for this well, e.g. "A".
          - *col*: The name of the column for this well, e.g. "1".
          - *row_i*: The row-index of this well, counting from 0.
          - *col_j*: The column-index of this well, counting from 0.
 
        If **data_loader** was provided but **merge_cols** was not:
 
        - **layout** (`pandas.DataFrame`) – See above.
 
        - **data** (`pandas.DataFrame`) – The concatenated result of calling 
          **data_loader()** on every path specified in the given TOML file.  
          See :func:`pandas.concat()` for more information on how the data from 
          different paths are concatenated.
 
        If **data_loader** and **merge_cols** were both provided:
 
        - **merged** (`pandas.DataFrame`) – The result of merging the 
          **layout** and **data** data frames along the columns specified by 
          **merge_cols**.  See :func:`pandas.merge()` for more details on the 
          merge itself.  The resulting data frame will have one or more rows 
          for each well (more are possible if there are multiple data points 
          per well, e.g. a time course), a column for each experimental 
          condition described in the TOML file, and a column for each kind of 
          data loaded from the data files.  

        If **meta** was requested:

        - **meta** (:class:`~wellmap.Meta`) – As described above.
    """

    try:
        ## Parse the TOML file:
        meta_requested = meta
        extras_requested = extras

        config, paths, concats, meta = config_from_toml(
                toml_path,
                path_guess=path_guess,
                on_alert=on_alert,
                path_required=path_required or data_loader,
        )

        def augment_return_value(*args):
            """
            Helper function to work out which values to return, depending on 
            whether or not the caller wants any information beyond the 
            layout itself.
            """
            if meta_requested:
                args += meta,

            if extras_requested:
                if meta_requested:
                    raise ValueError("Redundant to simultaneously request *meta* and *extras*")
                else:
                    warn("The *extras* argument to `wellmap.load()` is deprecated.  The *meta* argument should be used instead.\nhttps://wellmap.readthedocs.io/en/latest/deprecations.html#load-extras-deps", DeprecationWarning, stacklevel=3)
                    args += meta.extras,

            if report_dependencies:
                if meta_requested:
                    raise ValueError("Redundant to simultaneously request *meta* and *report_dependencies*")
                else:
                    warn("The *report_dependencies* argument to `wellmap.load()` is deprecated.  The *meta* argument should be used instead.\nhttps://wellmap.readthedocs.io/en/latest/deprecations.html#load-extras-deps", DeprecationWarning, stacklevel=3)
                    args += meta.dependencies,

            return args if len(args) != 1 else args[0]

        def get_extras_kwarg():
            """
            Helper function to determine whether or not to pass any "extras" 
            (i.e. key/value pairs in the TOML file requested by the caller) to 
            the **data_loader** function.
            """
            if (not extras_requested) and (not meta_requested):
                return {}

            sig = inspect.signature(data_loader)

            if 'extras' not in sig.parameters:
                return {}
            if sig.parameters['extras'].kind not in {
                    inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    inspect.Parameter.KEYWORD_ONLY,
            }:
                return {}

            return {'extras': meta.extras}

        layout = table_from_config(config, paths)
        layout = pd.concat([layout, *concats], sort=False)

        if path_required or data_loader:
            if 'path' not in layout:
                raise paths.missing_path_error

            # It shouldn't be possible for only some wells to have paths.
            assert not layout['path'].isnull().any()

        if len(layout) == 0:
            raise LayoutError("No wells defined.")

        ## Load the data associated with each well:
        if data_loader is None:
            if merge_cols is not None:
                raise ValueError("Specified columns to merge, but no function to load data!")
            return augment_return_value(layout)

        data = pd.DataFrame()

        for path in layout['path'].unique():
            df = data_loader(path, **get_extras_kwarg())
            df['path'] = path
            data = pd.concat([data, df], sort=False)

        ## Merge the layout and the data into a single data frame:
        if merge_cols is None:
            return augment_return_value(layout, data)

        if merge_cols is True:
            # Merge on any columns with matching names.  Complain if the only 
            # matching column is "path", because we made that column ourselves.

            kwargs = {
                'on': list(set(layout.columns) & set(data.columns))
            }
            if kwargs['on'] == ['path']:
                raise ValueError(f"No common columns (expect 'path') to perform merge on:\nlayout cols: {quoted_join(layout.columns)}\ndata cols: {quoted_join(data.columns)}")
        else:
            if not merge_cols:
                raise ValueError("Must specify at least one column to merge on (i.e. cannot specify empty `merge_cols` dict).")

            def check_merge_cols(cols, known_cols, attrs):
                unknown_cols = set(cols) - set(known_cols)
                if unknown_cols:
                    raise ValueError(f"Cannot merge on {quoted_join(unknown_cols)}.  Allowed {attrs} of the `merge_cols` dict: {quoted_join(known_cols)}.")
                return list(cols)

            left_ok = 'well', 'well0', 'row', 'col', 'row_i', 'col_i', 'plate'
            kwargs = {
                    'left_on': ['path'] + check_merge_cols(
                        merge_cols.keys(), left_ok, 'keys'),
                    'right_on': ['path'] + check_merge_cols(
                        merge_cols.values(), data.columns, 'values'),
            }

        merged = pd.merge(layout, data, **kwargs)
        return augment_return_value(merged)

    except LayoutError as err:
        err.toml_path = err.toml_path or toml_path
        raise

def config_from_toml(
        toml_path,
        *,
        shift=(0,0),
        path_guess=None,
        path_required=False,
        on_alert=None,
):
    """
    Create a config dictionary from the given TOML file.

    This function is mostly responsible for interpreting the various [meta] 
    settings.
    """
    toml_path = Path(toml_path).resolve()

    with open(toml_path, 'rb') as f:
        toml_data = tomllib.load(f)

    config = configdict(shift_config(toml_data, shift))
    paths = PathManager(
            config.meta.get('path'),
            config.meta.get('paths'),
            toml_path,
            path_guess,
    )
    concats = []
    meta = Meta(
            extras=config.user,
            dependencies={toml_path},
            style=Style(),
    )

    if 'style' in config.meta or 'param_styles' in config.meta:
        # Need to do this before handling any included layouts.
        try:
            meta.style = Style(
                    **config.meta.get('style', {}),
                    by_param=config.meta.get('param_styles', {}),
            )
        except StyleAttributeError as err:
            raise err.as_layout_error() from None

    def iter_include_paths():

        def _iter_include_paths(meta, top_level=True, list_index=0):
            if isinstance(meta, str):
                yield meta, (0, 0)

            elif isinstance(meta, dict):
                try:
                    path = meta['path']
                except KeyError:
                    raise LayoutError("if 'meta.include' is a dictionary, it must have a 'path' key")

                try:
                    shift_str = meta['shift']
                except KeyError:
                    shift = (0, 0)
                else:
                    shift = parse_shift(shift_str)

                yield path, shift

            elif top_level and isinstance(meta, list):
                # Yield the paths in reverse order so that later paths take 
                # precedence over earlier paths.  This is needed because 
                # `recursive_merge()` by default does not overwrite values, so 
                # the values that are merged first take precedence.
                for i, m in enumerate(reversed(meta)):
                    yield from _iter_include_paths(m, top_level=False, list_index=i)

            else:
                if top_level:
                    raise LayoutError(f"expected 'meta.include' to be string, list, or dictionary, not: {meta!r}")
                else:
                    raise LayoutError(f"expected 'meta.include[{list_index}]' to be string or dictionary, not: {meta!r}")

        meta = config.meta.get('include', [])
        for rel_path, rel_shift in _iter_include_paths(meta):
            abs_path = resolve_path(toml_path, rel_path)
            abs_shift = add_shifts(shift, rel_shift)
            yield abs_path, abs_shift

    for subpath, subshift in iter_include_paths():
        # The [meta.path] field in included files is currently ignored.  Not 
        # for any philosophical reason, just because it would be tricky to 
        # implement (and not very useful).  Note that the *path_required* 
        # argument isn't provided to the recursive call; this is why.
        subconfig, _, subconcats, submeta = config_from_toml(
                subpath,
                shift=subshift,
                on_alert=on_alert,
        )
        recursive_merge(config, subconfig)
        concats += subconcats
        recursive_merge(meta.extras, submeta.extras)
        meta.dependencies |= {subpath, *submeta.dependencies}
        meta.style.merge(submeta.style)

    def iter_concat_paths():
        try:
            paths = config.meta['concat']
        except KeyError:
            yield from []
            return

        if isinstance(paths, str):
            paths = [(None, paths)]
        elif isinstance(paths, list):
            paths = [(None, x) for x in paths]
        elif isinstance(paths, dict):
            paths = paths.items()
        else:
            raise LayoutError(f"expected 'meta.concat' to be string, list, or dictionary, not: {paths!r}")

        for plate_name, path in paths:
            yield plate_name, resolve_path(toml_path, path)

    for plate_name, path in iter_concat_paths():
        df, submeta = load(
                path,
                path_guess=path_guess,
                path_required=path_required,
                meta=True,
                on_alert=on_alert,
        )
        if plate_name:
            df['plate'] = plate_name

        concats.append(df)
        meta.dependencies |= {path, *submeta.dependencies}
        # Should do something with style and extras, see #37.

    if 'alert' in config.meta:
        if on_alert:
            on_alert(toml_path, config.meta['alert'])
        else:
            try: print(f"{toml_path.relative_to(Path.cwd())}:", file=sys.stderr)
            except ValueError: print(f"{toml_path}:", file=sys.stderr)
            print(config.meta['alert'], file=sys.stderr)

    config.pop('meta', None)
    return config, paths, concats, meta

def shift_config(config, shift):
    if shift == (0, 0):
        return config

    shifted_config = {}

    f = lambda d: shift_pattern(d, shift)
    def cant_shift_irow_icol():
        raise LayoutError("can't use 'meta.include.shift' on layouts that use [irow] and/or [icol]")

    shifters = {
            'plate':    lambda d: {
                k: shift_config(v, shift)
                for k, v in d.items()
            },
            'row':      lambda d: map_keys(d, f),
            'irow':     lambda d: cant_shift_irow_icol(),
            'col':      lambda d: map_keys(d, f),
            'icol':     lambda d: cant_shift_irow_icol(),
            'block':    lambda d: map_keys(d, f, level=1),
            'well':     lambda d: map_keys(d, f),
    }
    for k, v in config.items():
        shifter = shifters.get(k, lambda d: d)
        shifted_config[k] = shifter(v)

    return shifted_config

def table_from_config(config, paths):
    config = configdict(config)

    if not config.plates:
        wells = wells_from_config(config)
        # Getting the index can raise errors we might not care about if there 
        # aren't any wells (e.g. it doesn't matter if a path doesn't exist if 
        # it won't be associated with any wells).  Skipping the call is a bit 
        # of a hacky way to avoid these errors, but it works.
        index = paths.get_index_for_only_plate() if wells else {}
        return table_from_wells(wells, index)

    else:
        tables = []
        paths.check_named_plates(config.plates)

        for key, plate_config in config.plates.items():
            if not isinstance(plate_config, dict):
                raise LayoutError(f"Illegal attribute '{key}' within [plate] block but outside of any plates.")
            if 'expt' in plate_config:
                raise LayoutError("Cannot use [expt] in [plate] blocks.")

            # Mold the plate dictionary into the same format as the top-level 
            # dictionary, i.e. the format expected by wells_from_config(), by 
            # putting any global parameters into the 'expt' block.  Copy to 
            # avoid infinite recursion.
            plate_config = plate_config.copy()
            plate_config['expt'] = configdict(plate_config).user

            plate_config = recursive_merge(plate_config, config)
            wells = wells_from_config(plate_config)

            index = paths.get_index_for_named_plate(key) if wells else {}
            tables += [table_from_wells(wells, index)]

        # Make an effort to keep the columns in a reasonable order.  I don't 
        # know why `pd.concat()` doesn't do this on its own...
        cols = tables[-1].columns
        return pd.concat(tables, sort=False)[cols]

def wells_from_config(config):
    config = configdict(config)
    wells = {}

    def iter_wells(config):
        for key in config:
            for ij in iter_well_indices(key):
                yield ij, config[key]

    def iter_rows(config):
        for key in config:
            for i in iter_row_indices(key):
                yield i, config[key]

    def iter_cols(config):
        for key in config:
            for j in iter_col_indices(key):
                yield j, config[key]

    ## Create and fill in wells defined by 'well' blocks.
    for ij, subconfig in iter_wells(config.wells):
        wells.setdefault(ij, {})
        recursive_merge(wells[ij], subconfig, overwrite=True)

    ## Create new wells implied by any 'block' blocks:
    blocks = {}
    pattern = re.compile(r'(\d+)x(\d+)')

    for size in config.blocks:
        match = pattern.match(size)
        if not match:
            raise LayoutError(f"Unknown [block] size '{size}', expected 'WxH' (where W and H are both positive integers).")

        width, height = map(int, match.groups())
        if width == 0:
            raise LayoutError(f"[block.{size}] has no width.  No wells defined.")
        if height == 0:
            raise LayoutError(f"[block.{size}] has no height.  No wells defined.")

        for top_left, subconfig in iter_wells(config.blocks[size]):
            for ij in iter_ij_in_block(top_left, width, height):
                block = width * height, deepcopy(subconfig)
                blocks.setdefault(ij, [])
                blocks[ij].insert(0, block)
                wells.setdefault(ij, {})
    
    ## Create new wells implied by any 'row' & 'col' blocks.

    def simplify_keys(dim):
        before = config.get(dim, {})
        after = {}
        iter = {
                'row': iter_rows,
                'col': iter_cols,
                'irow': iter_rows,
                'icol': iter_cols,
        }
        
        for a, subconfig in iter[dim](before):
            after.setdefault(a, {})
            recursive_merge(after[a], subconfig, overwrite=True)

        return after

    def sanity_check(dim1, dim2, span):
        if config.get(dim1) and not span:
            raise LayoutError(f"Found {plural(config[dim1]):# [{dim1}] spec/s}, but no {dim2}.  No wells defined.")

    rows = simplify_keys('row')
    cols = simplify_keys('col')
    irows = simplify_keys('irow')
    icols = simplify_keys('icol')

    occupied_non_irow_rows = range_from_indices(
            *(i for i,j in wells.keys()),
            *rows.keys(),
    )
    occupied_non_icol_cols = range_from_indices(
            *(j for i,j in wells.keys()),
            *cols.keys(),
    )
    occupied_rows = range_from_indices(
            *occupied_non_irow_rows,
            *(interleave(ii,j) for ii,j in itertools.product(
                irows.keys(), occupied_non_icol_cols))
    )
    occupied_cols = range_from_indices(
            *occupied_non_icol_cols,
            *(interleave(jj,i) for i,jj in itertools.product(
                occupied_non_irow_rows, icols.keys()))
    )

    sanity_check('row', 'columns', occupied_cols)
    sanity_check('irow', 'columns', occupied_cols)
    sanity_check('col', 'rows', occupied_rows)
    sanity_check('icol', 'rows', occupied_rows)

    for ij in itertools.product(rows, occupied_cols):
        wells.setdefault(ij, {})
    for ij in itertools.product(occupied_rows, cols):
        wells.setdefault(ij, {})
    for ii, j in itertools.product(irows, occupied_cols):
        ij = interleave(ii, j), j
        wells.setdefault(ij, {})
    for i, jj in itertools.product(occupied_rows, icols):
        ij = i, interleave(jj, i)
        wells.setdefault(ij, {})

    ## Fill in any wells created above.
    for ij in wells:
        i, j = ij
        ii = interleave(i, j)
        jj = interleave(j, i)

        # Merge in order of precedence: [block], [row/col], top-level.
        # [well] is already accounted for.
        blocks_by_area = sorted(blocks.get(ij, []), key=lambda x: x[0])
        for area, block in blocks_by_area:
            recursive_merge(wells[ij], block)

        recursive_merge(wells[ij], rows.get(i, {}))
        recursive_merge(wells[ij], cols.get(j, {}))
        recursive_merge(wells[ij], irows.get(ii, {}))
        recursive_merge(wells[ij], icols.get(jj, {}))
        recursive_merge(wells[ij], config.expt)

    return wells
    
def table_from_wells(wells, index):
    table = []
    user_cols = []
    max_j = max([12] + [j for i,j in wells])
    digits = len(str(max_j + 1))
    
    for i, j in wells:
        row, col = row_col_from_ij(i, j)
        well = well_from_ij(i, j)
        well0 = well0_from_well(well, digits=digits)
        user_cols += [x for x in wells[i,j] if x not in user_cols]

        table += [{
                **wells[i,j],
                **index,
                'well': well,
                'well0': well0,
                'row': row, 'col': col,
                'row_i': i, 'col_j': j,
        }]

    # Make an effort to put the columns in a reasonable order:
    columns = ['well', 'well0', 'row', 'col', 'row_i', 'col_j']
    columns += list(index) + user_cols

    return pd.DataFrame(table, columns=columns)

def resolve_path(parent_path, child_path):
    parent_dir = Path(parent_path).parent
    child_path = Path(child_path)

    if child_path.is_absolute():
        return child_path
    else:
        return parent_dir / child_path

@dataclass
class Meta:
    """
    Miscellaneous information that was present in the TOML file(s) but not part 
    of the layout itself.

    The only way to get an instance of this class is by calling `load` with the 
    ``meta=True`` argument.  You should never instantiate this class directly.
    """

    extras: Dict[str, Any]
    """
    A dictionary containing any key/value pairs present in the TOML file but 
    not part of the layout.  See the :ref:`file format reference <extras>` for 
    more information.
    """

    dependencies: Set[Path]
    """
    A set containing absolute paths to every layout file that was referenced by 
    **toml_path**.  This includes **toml_path** itself, and the paths to any 
    `included <meta.include>` or `concatenated <meta.concat>` layout files.  It 
    does not include paths to `data files <meta.path>`, as these are already 
    listed in the *path* column of the loaded data frame.  You can use this 
    information in analysis scripts, in conjunction with `os.path.getmtime`, to 
    reliably determine whether or not the layout could have changed, e.g. 
    before repeating an expensive analysis.
    """

    style: Style
    """
    A `Style` object describing how the layout requests to be plotted.  The 
    information in this object comes from `meta.style` and `meta.param_styles`.
    """

class PathManager:

    def __init__(self, path, paths, toml_path, path_guess=None):
        self.path = path
        self.paths = paths
        self.toml_path = Path(toml_path)
        self.path_guess = path_guess
        self.missing_path_error = None

    def __str__(self):
        return str({
            'path': self.path,
            'paths': self.paths,
            'toml_path': self.toml_path,
            'path_guess': self.path_guess,
        })

    def check_overspecified(self):
        if self.path and self.paths:
            raise LayoutError("Both `meta.path` and `meta.paths` specified; ambiguous.")

    def check_named_plates(self, names):
        self.check_overspecified()

        if self.path is not None:
            raise LayoutError(f"`meta.path` specified with one or more [plate] blocks ({quoted_join(names)}).  Did you mean to use `meta.paths`?")

        if isinstance(self.paths, dict):
            if set(names) != set(self.paths):
                raise LayoutError(f"The keys in `meta.paths` ({quoted_join(sorted(self.paths))}) don't match the [plate] blocks ({quoted_join(sorted(names))})")
        
    def get_index_for_only_plate(self):
        # If there is only one plate:
        # - Have `paths`: Ambiguous, complain.
        # - Have `path`: Use it, complain if non-existent
        # - Have extension: Guess path from stem, complain if non-existent.
        # - Don't have anything: Don't put path in the index

        def make_index(path):
            path = resolve_path(self.toml_path, path)
            if not path.exists():
                raise LayoutError(f"'{path}' does not exist")
            return {'path': path}

        self.check_overspecified()

        if self.paths is not None:
            raise LayoutError(f"`meta.paths` ({self.paths if isinstance(self.paths, str) else quoted_join(self.paths)}) specified without any [plate] blocks.  Did you mean to use `meta.path`?")

        if self.path is not None:
            return make_index(self.path)

        if self.path_guess:
            return make_index(self.path_guess.format(self.toml_path))

        self.missing_path_error = LayoutError("Analysis requires a data file, but none was specified and none could be inferred.  Did you mean to set `meta.path`?")
        return {}

    def get_index_for_named_plate(self, name):
        # If there are multiple plates:
        # - Have `path`: Ambiguous, complain.
        # - `paths` is string: Format with name, complain if non-existent or 
        #   if formatting didn't change the path.
        # - `paths` is dict: Make sure the keys match the plates in the config.  
        #   Look up the path, complain if non-existent.
        # - Don't have `paths`: Put the name in the index without a path.
        
        def make_index(name, path):
            path = resolve_path(self.toml_path, path)
            if not path.exists():
                raise LayoutError(f"'{path}' for plate '{name}' does not exist")
            return {'plate': name, 'path': path}

        if self.paths is None:
            self.missing_path_error = LayoutError("Analysis requires a data file for each plate, but none were specified.  Did you mean to set `meta.paths`?")
            return {'plate': name}

        if isinstance(self.paths, str):
            return make_index(name, self.paths.format(name))

        if isinstance(self.paths, dict):
            if name not in self.paths:
                raise LayoutError(f"No data file path specified for plate '{name}'")
            return make_index(name, self.paths[name])

        raise LayoutError(f"Expected `meta.paths` to be dict or str, got {type(self.paths)}: {self.paths}")

class configdict(dict):
    special = {
            'meta': 'meta',
            'plates': 'plate',
            'rows': 'row',
            'irows': 'irow',
            'cols': 'col',
            'icols': 'icol',
            'blocks': 'block',
            'wells': 'well',
            'expt': 'expt',
    }

    def __init__(self, config):
        self.update(config)

    def __getattr__(self, key):
        if key in self.special:
            return self.setdefault(self.special[key], {})

    def __setattr__(self, key, value):
        if key in self.special:
            self[self.special[key]] = value

    @property
    def user(self):
        return {k: v
                for k, v in self.items()
                if k not in self.special.values()
        }

