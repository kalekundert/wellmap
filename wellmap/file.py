#!/usr/bin/env python3

import toml
import sys, re, itertools, inspect
import pandas as pd
from pathlib import Path
from inform import plural
from copy import deepcopy
from .util import *

# Data Structures
# ===============
# `config`
#   A direct reflection of the TOML input file.  Arbitrary parameters can be 
#   specified on a per-experiment, per-plate, per-row, per-column, or per-well 
#   basis.  
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

def load(toml_path, *, data_loader=None, merge_cols=None, path_guess=None, 
        path_required=False, extras=None, report_dependencies=False, 
        on_alert=None):
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
        Indicates that `load()` should attempt to merge the plate layout and 
        the actual data associated with it into a single data frame.  This 
        functionality requires several conditions to be met:
       
        1. The **data_loader** argument must be specified (otherwise there'd be 
           no data to merge).

        2. The data frame returned by **data_loader()** must be `"tidy"`__.  
           Briefly, a data frame is tidy if each of its columns represents a 
           single variable (e.g.  time, fluorescence) and each of its rows 
           represents a single observation.  
            
           __ http://vita.had.co.nz/papers/tidy-data.html

        3. The data frame returned by **data_loader()** must have one (or more) 
           columns/variables indicating which well each row/observation comes 
           from.  For example, a column called "Well" with values like "A1", 
           "A2", "B1", "B2", etc. would satisfy this requirement.
        
        The **merge_cols** argument specifies which columns to use when merging 
        the data frames representing the layout and the actual data (i.e. the 
        two data frames that would be returned if **data_loader** was specified 
        but **merge_cols** was not) into one.  The argument can either be a 
        bool or a dictionary:

        If *False* (or falsey, e.g. ``None``, ``{}``, etc.), the data frames 
        will be returned separately and not be merged.  This is the default 
        behavior.

        If *True*, the data frames will be merged using any columns that share 
        the same name.  For example, the layout will always have a column named 
        *well*, so if the actual data also has a column named *well*, the merge 
        would happen on those columns.

        If a dictionary, the keys and values identify the names of the columns 
        that correspond with each other for the purpose of merging.  Each key 
        should be one of the columns from the data frame representing the 
        layout loaded from the TOML file.  This data frame has 8 columns which 
        identify the wells: *plate*, *path*, *well*, *well0*, *row*, *col*, 
        *row_i*, *row_j*.  See the "Returns" section below for more details on 
        the differences between these columns.  Note that the *path* column is 
        included in the merge automatically and never has to be specified.  
        Each value should be one of the columns from the data frame 
        representing the actual data.  This data frame will have whatever 
        columns were created by **data_loader()**.  

        Note that the columns named in each key-value pair must contain values 
        that correspond exactly (i.e. not "A1" and "A01").  It is the 
        responsibility of **data_loader()** to ensure that this is possible.
       
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

    :param str,list extras:
        One or more keys to extract directly from the given TOML file.  
        Typically, this would be used to get information pertaining to the 
        whole analysis and not any wells in particular (e.g. instruments used, 
        preferred algorithms, plotting parameters, etc.).  Either one key 
        (string) or multiple keys (list of strings) can be specified.  `Dotted 
        keys <https://github.com/toml-lang/toml#keys>`__ are supported.  
        Specifying this argument causes the value(s) corresponding to the given 
        key(s) to be returned, see below.

    :param bool report_dependencies:
        If true, return a set of all the TOML files that were read in the 
        process of loading the layout from the given **toml_path**.  See the 
        description of **dependencies** below for more details.  You can use 
        this information in analysis scripts (e.g. in conjunction with 
        :func:`os.path.getmtime`) to avoid repeating expensive analyses if the 
        underlying layout hasn't changed.

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
          
        If **extras** was provided:
 
        - **extras** – The value(s) corresponding to the specified "extra" 
          key(s).  If only one extra key was specified, only that value will be 
          returned.  If multiple extra keys were specified, a `dict` containing 
          the value for each such key will be returned.  For example, consider 
          the following TOML file::
 
              a = 1
              b = 2
 
          If we were to load this file with ``extras='a'``, this return 
          value would simply be ``1``.  With ``extras=['a', 'b']``, the same 
          return value would be ``{'a': 1, 'b': 2}`` instead.

        If **report_dependencies** was provided:

        - **dependencies** – A set containing absolute paths to every layout 
          file that was referenced by **toml_path**.  This includes 
          **toml_path** itself, and the paths to any `included <meta.include>` 
          or `concatenated <meta.concat>` layout files.  It does not include 
          paths to `data files <meta.path>`, as these are included already in 
          the *path* column of the **layout** or **merged** data frames.
    """

    try:
        ## Parse the TOML file:
        config, paths, concats, extras, deps = config_from_toml(
                toml_path,
                path_guess=path_guess,
                extra_keys=extras,
                on_alert=on_alert,
        )

        def add_extras(*args, include_deps=True):
            """
            Helper function to work out which values to return, depending on 
            whether or not the caller wants any "extras" (i.e. key/value pairs 
            in the TOML file that wouldn't otherwise be parsed) or "deps" (i.e. 
            all the layout files that this one depends on).
            """
            if len(extras) == 1:
                args += list(extras.values())[0],
            if len(extras) > 1:
                args += extras,

            if include_deps and report_dependencies:
                args += deps,

            return args if len(args) != 1 else args[0]

        def get_extras_kwarg():
            """
            Helper function to determine whether or not to pass any "extras" 
            (i.e. key/value pairs in the TOML file requested by the caller) to 
            the **data_loader** function.
            """
            if not extras:
                return {}

            sig = inspect.signature(data_loader)

            if 'extras' not in sig.parameters:
                return {}
            if sig.parameters['extras'].kind != inspect.Parameter.POSITIONAL_OR_KEYWORD:
                return {}

            return {'extras': add_extras(include_deps=False)}

        layout = table_from_config(config, paths)
        layout = pd.concat([layout, *concats], sort=False)

        if path_required or data_loader:
            if 'path' not in layout or layout['path'].isnull().any():
                raise paths.missing_path_error

        if len(layout) == 0:
            raise ConfigError("No wells defined.")

        ## Load the data associated with each well:
        if data_loader is None:
            if merge_cols is not None:
                raise ValueError("Specified columns to merge, but no function to load data!")
            return add_extras(layout)

        data = pd.DataFrame()

        for path in layout['path'].unique():
            df = data_loader(path, **get_extras_kwarg())
            df['path'] = path
            data = data.append(df, sort=False)

        ## Merge the layout and the data into a single data frame:
        if not merge_cols:
            return add_extras(layout, data)

        if merge_cols is True:
            # Let pandas choose which columns to merge on.
            kwargs = {}
        else:
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
        return add_extras(merged)

    except ConfigError as err:
        err.toml_path = toml_path
        raise

def config_from_toml(toml_path, *, path_guess=None, extra_keys=None, on_alert=None):
    toml_path = Path(toml_path).resolve()
    config = configdict(toml.load(str(toml_path)))
    concats = []
    deps = {toml_path}

    def iter_extra_keys():
        if extra_keys is None:
            return
        elif isinstance(extra_keys, str):
            yield extra_keys
        else:
            yield from extra_keys

    def iter_include_paths():
        try:
            paths = config.meta['include']
        except KeyError:
            yield from []
            return

        if isinstance(paths, str):
            paths = [paths]
        elif isinstance(paths, list):
            pass
        else:
            raise ConfigError(f"expected 'meta.include' to be string or list, not {paths!r}")

        # Yield the paths in reverse order so that later paths take precedence 
        # over earlier paths.  This is needed because `recursive_merge()` by 
        # default does not overwrite values, so the values that are merged 
        # first take precedence.
        for path in reversed(paths):
            yield resolve_path(toml_path, path)

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
            raise ConfigError(f"expected 'meta.concat' to be string, list, or dictionary, not {paths!r}")

        for plate_name, path in paths:
            yield plate_name, resolve_path(toml_path, path)

    # Find any specific fields requested by the caller.
    extras = {}
    for key in iter_extra_keys():
        try: extras[key] = get_dotted_key(config, key)
        except KeyError: pass

    # Synthesize any available path information.
    paths = PathManager(
            config.meta.get('path'),
            config.meta.get('paths'),
            toml_path,
            path_guess,
    )

    # Include one or more remote files if any are specified.  
    for path in iter_include_paths():
        subconfig, _, subconcats, subextras, subdeps = config_from_toml(
                path,
                extra_keys=extra_keys,
                on_alert=on_alert,
        )
        recursive_merge(config, subconfig)
        recursive_merge(extras, subextras)
        concats += subconcats
        deps |= {path, *subdeps}

    # Load any files to be concatenated.
    for plate_name, path in iter_concat_paths():
        df, subdeps = load(
                path,
                path_guess=path_guess,
                report_dependencies=True,
                on_alert=on_alert,
        )
        if plate_name: df['plate'] = plate_name
        deps |= {path, *subdeps}
        concats.append(df)

    # Print out any messages contained in the file.
    if 'alert' in config.meta:
        if on_alert:
            on_alert(toml_path, config.meta['alert'])
        else:
            try: print(f"{toml_path.relative_to(Path.cwd())}:", file=sys.stderr)
            except ValueError: print(f"{toml_path}:", file=sys.stderr)
            print(config.meta['alert'], file=sys.stderr)

    config.pop('meta', None)
    return config, paths, concats, extras, deps

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
                raise ConfigError(f"Illegal attribute '{key}' within [plate] block but outside of any plates.")
            if 'expt' in plate_config:
                raise ConfigError("Cannot use [expt] in [plate] blocks.")

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
        if ij in wells:
            raise ConfigError(f"[well.{well_from_ij(*ij)}] defined more than once.")
        wells[ij] = deepcopy(subconfig)

    ## Create new wells implied by any 'block' blocks:
    blocks = {}
    pattern = re.compile(r'(\d+)x(\d+)')

    for size in config.blocks:
        match = pattern.match(size)
        if not match:
            raise ConfigError(f"Unknown [block] size '{size}', expected 'WxH' (where W and H are both positive integers).")

        width, height = map(int, match.groups())
        if width == 0:
            raise ConfigError(f"[block.{size}] has no width.  No wells defined.")
        if height == 0:
            raise ConfigError(f"[block.{size}] has no height.  No wells defined.")

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
            recursive_merge(after[a], subconfig)

        return after

    def sanity_check(dim1, *dim2s):
        if config.get(dim1) \
                and not wells \
                and not blocks \
                and not any(config.get(x) for x in dim2s):
            raise ConfigError(f"Found {plural(config[dim1]):# [{dim1}] spec/s}, but no [{'/'.join(dim2s)}] specs.  No wells defined.")

    rows = simplify_keys('row')
    cols = simplify_keys('col')
    irows = simplify_keys('irow')
    icols = simplify_keys('icol')

    sanity_check('row', 'col', 'icol')
    sanity_check('col', 'row', 'irow')
    for ij in itertools.product(rows, cols):
        wells.setdefault(ij, {})

    sanity_check('irow', 'col')
    for ii, j in itertools.product(irows, cols):
        ij = interleave(ii, j), j
        wells.setdefault(ij, {})

    sanity_check('icol', 'row')
    for i, jj in itertools.product(rows, icols):
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


def recursive_merge(config, defaults, overwrite=False):
    for key, default in defaults.items():
        if isinstance(default, dict):
            if isinstance(config.get(key, {}), dict):
                config.setdefault(key, {})
                recursive_merge(config[key], default, overwrite)
            elif overwrite:
                config[key] = deepcopy(default)
        else:
            if overwrite or key not in config:
                config[key] = default

    # Modified in-place, but also returned for convenience.
    return config

def resolve_path(parent_path, child_path):
    parent_dir = Path(parent_path).parent
    child_path = Path(child_path)

    if child_path.is_absolute():
        return child_path
    else:
        return parent_dir / child_path

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
            raise ConfigError(f"Both `meta.path` and `meta.paths` specified; ambiguous.")

    def check_named_plates(self, names):
        self.check_overspecified()

        if self.path is not None:
            raise ConfigError(f"`meta.path` specified with one or more [plate] blocks ({quoted_join(names)}).  Did you mean to use `meta.paths`?")

        if isinstance(self.paths, dict):
            if set(names) != set(self.paths):
                raise ConfigError(f"The keys in `meta.paths` ({quoted_join(sorted(self.paths))}) don't match the [plate] blocks ({quoted_join(sorted(names))})")
        
    def get_index_for_only_plate(self):
        # If there is only one plate:
        # - Have `paths`: Ambiguous, complain.
        # - Have `path`: Use it, complain if non-existent
        # - Have extension: Guess path from stem, complain if non-existent.
        # - Don't have anything: Don't put path in the index

        def make_index(path):
            path = resolve_path(self.toml_path, path)
            if not path.exists():
                raise ConfigError(f"'{path}' does not exist")
            return {'path': path}

        self.check_overspecified()

        if self.paths is not None:
            raise ConfigError(f"`meta.paths` ({self.paths if isinstance(self.paths, str) else quoted_join(self.paths)}) specified without any [plate] blocks.  Did you mean to use `meta.path`?")

        if self.path is not None:
            return make_index(self.path)

        if self.path_guess:
            return make_index(self.path_guess.format(self.toml_path))

        self.missing_path_error = ConfigError(f"Analysis requires a data file, but none was specified and none could be inferred.  Did you mean to set `meta.path`?")
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
                raise ConfigError(f"'{path}' for plate '{name}' does not exist")
            return {'plate': name, 'path': path}

        if self.paths is None:
            self.missing_path_error = ConfigError(f"Analysis requires a data file for each plate, but none were specified.  Did you mean to set `meta.paths`?")
            return {'plate': name}

        if isinstance(self.paths, str):
            return make_index(name, self.paths.format(name))

        if isinstance(self.paths, dict):
            if name not in self.paths:
                raise ConfigError(f"No data file path specified for plate '{name}'")
            return make_index(name, self.paths[name])

        raise ConfigError(f"Expected `meta.paths` to be dict or str, got {type(self.paths)}: {self.paths}")

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



