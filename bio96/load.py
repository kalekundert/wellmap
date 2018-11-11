#!/usr/bin/env python3

import toml
import re, itertools
import pandas as pd
from pathlib import Path
from .util import *

# Data Structures
# ===============
# `config`
#   A direct reflection of the TOML input file.  Arbitrary parameters can be 
#   specified on a per-experiment, per-plate, per-row, per-column, or per-well 
#   basis.  
#
# `wells`
#   Dictionary where the keys are well identifiers (e.g. "A1", "B2", etc.) and 
#   the values are dictionaries containing arbitrary information about said 
#   well.  This is basically a version of the `config` data structure where 
#   all the parameters have been resolved to a per-well basis.
#
# `table`
#   A pandas DataFrame derived from the `wells` data structure.  Each row 
#   represents a well, and each column represents one of the fields in the well 
#   dictionaries.  Columns identifying the plate and well are also added.

def load(toml_path, path_guess=None, path_required=False,
        data_loader=None, merge_cols=None):

    # Parse the TOML file:
    config, paths = config_from_toml(toml_path, path_guess,
            path_required or data_loader)
    labels = table_from_config(config, paths)

    # Load the data associated with each well.
    if data_loader is None:
        if merge_cols is not None:
            raise ValueError("Specified columns to merge, but no function to load data!")
        return labels

    data = pd.DataFrame()

    for path in labels['path'].unique():
       df = data_loader(path)
       df['path'] = path
       data = data.append(df)

    # Merge the labels and the data into a single data frame.
    if merge_cols is None:
        return labels, data

    def check_merge_cols(cols, known_cols, attr):
        unknown_cols = set(cols) - set(known_cols)
        if unknown_cols:
            raise ValueError("Cannot merge on {','.join(unknown_cols)}.  `merge_cols` {attr} must be in {','.join(known_cols)}.")
        return list(cols)

    left_ok = 'well', 'row', 'col', 'row_i', 'col_i'
    left_on = check_merge_cols(merge_cols.keys(), left_ok, 'keys')
    right_on = check_merge_cols(merge_cols.values(), data.columns, 'values')

    return pd.merge(
            labels, data,
            left_on=left_on + ['path'],
            right_on=right_on + ['path'],
    )

def config_from_toml(toml_path, path_guess=None, require_path=False):
    toml_path = Path(toml_path).resolve()
    config = configdict(toml.load(str(toml_path)))

    # Synthesize any available path information.
    paths = PathManager(
            config.meta.get('path'),
            config.meta.get('paths'),
            toml_path,
            path_guess,
            require_path,
    )

    # Include one or more remote files if any are specified.  
    if 'include' in config.meta:
        includes = config.meta['include']
        if isinstance(includes, str):
            includes = [includes]

        for include in reversed(includes):
            path = resolve_path(toml_path, include)
            defaults, _ = config_from_toml(path)
            recursive_merge(config, defaults)

    # Print out any messages contained in the file.
    if 'alert' in config.meta:
        print(config.meta['alert'])

    config.pop('meta', None)
    return config, paths

def table_from_config(config, paths):
    config = configdict(config)

    if not config.plates:
        wells = wells_from_config(config)
        index = paths.get_index_for_only_plate()
        return table_from_wells(wells, index)

    else:
        tables = []
        paths.check_named_plates(config.plates)

        for key, plate_config in config.plates.items():
            # Copy to avoid infinite recursion.
            plate_config = recursive_merge(plate_config.copy(), config)
            wells = wells_from_config(plate_config)

            index = paths.get_index_for_named_plate(key)
            tables += [table_from_wells(wells, index)]

        # Make an effort to keep the columns in a reasonable order.  I don't 
        # know why `pd.concat()` doesn't do this on its own...
        cols = tables[-1].columns
        return pd.concat(tables, sort=True)[cols]

def wells_from_config(config, label=None):
    config = configdict(config)
    wells = config.wells.copy()

    # Create new wells implied by any 'block' blocks:
    blocks = {}
    pattern = re.compile('(\d+)x(\d+)')

    for size in config.blocks:
        match = pattern.match(size)
        if not match:
            raise ConfigError("unknown block size '{size}', expected 'WxH' (where W and H are both positive integers).")

        width, height = map(int, match.groups())
        for top_left in config.blocks[size]:
            for key in iter_wells_in_block(top_left, width, height):
                wells.setdefault(key, {})
                blocks.setdefault(key, [])
                blocks[key].append(config.blocks[size][top_left])
    
    # Create new wells implied by any 'row' & 'col' blocks.
    for row, col in itertools.product(config.rows, config.cols):
        key = well_from_row_col(row, col)
        wells.setdefault(key, {})

    for irow, col in itertools.product(config.irows, config.cols):
        key = well_from_irow_col(irow, col)
        wells.setdefault(key, {})

    for row, icol in itertools.product(config.rows, config.icols):
        key = well_from_row_icol(row, icol)
        wells.setdefault(key, {})

    # Fill in any wells created above.
    for key in wells:
        row, col = row_col_from_well(key)
        irow, icol = irow_icol_from_well(key)

        # Merge in order of precedence: [block], [row/col], top-level
        for block in blocks.get(key, {}):
            recursive_merge(wells[key], block)

        recursive_merge(wells[key], config.rows.get(row, {}))
        recursive_merge(wells[key], config.cols.get(col, {}))
        recursive_merge(wells[key], config.irows.get(irow, {}))
        recursive_merge(wells[key], config.icols.get(icol, {}))
        recursive_merge(wells[key], config.user)

    return wells
    
def table_from_wells(wells, index):
    table = []
    user_cols = []

    for key in wells:
        row, col = row_col_from_well(key)
        row_i, col_j = ij_from_well(key)
        user_cols += [x for x in wells[key] if x not in user_cols]

        table += [{
                **wells[key],
                **index,
                'well': key,
                'row': row, 'col': col,
                'row_i': row_i, 'col_j': col_j,
        }]

    # Make an effort to put the columns in a reasonable order:
    columns = ['well', 'row', 'col', 'row_i', 'col_j']
    columns += list(index) + user_cols

    return pd.DataFrame(table, columns=columns)


def recursive_merge(config, defaults, overwrite=False):
    for key, default in defaults.items():
        if isinstance(default, dict):
            if isinstance(config.get(key, {}), dict):
                config.setdefault(key, {})
                recursive_merge(config[key], default, overwrite)
            elif overwrite:
                config[key] = default.copy()
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

    def __init__(self, path, paths, toml_path, path_guess=None, path_required=False):
        self.path = path
        self.paths = paths
        self.toml_path = Path(toml_path)
        self.path_guess = path_guess
        self.path_required = path_required

    def __str__(self):
        return str({
            'path': self.path,
            'paths': self.paths,
            'toml_path': self.toml_path,
            'path_guess': self.path_guess,
            'path_required': self.path_required,
        })

    def check_overspecified(self):
        if self.path and self.paths:
            raise ConfigError("{self.toml_path} specified both `meta.path` and `meta.paths`; ambiguous.")

    def check_named_plates(self, names):
        self.check_overspecified()

        if self.path is not None:
            raise ConfigError(f"'{self.toml_path}' specifies `meta.path`, but also one or more `[plate]` blocks ({','.join(names)}).  Did you mean to use `meta.paths`?")

        if isinstance(self.paths, dict):
            if set(names) != set(self.paths):
                raise ConfigError("The keys in `meta.paths` ({','.join(sorted(self.paths))}) don't match the `[plate]` blocks ({','.join(sorted(names))})")
        
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
            raise ConfigError(f"'{self.toml_path}' specifies `meta.paths` ({self.paths if isinstance(self.paths, str) else ','.join(self.paths)}), but no `[plate]` blocks.  Did you mean to use `meta.path`?")

        if self.path is not None:
            return make_index(self.path)

        if self.path_guess:
            return make_index(self.path_guess.format(self.toml_path))

        if self.path_required:
            raise ConfigError(f"'{self.toml_path}' doesn't specify a path to any data files.")

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
            if self.path_required:
                raise ConfigError(f"'{self.toml_path}' doesn't specify paths to any data files.")
            else:
                return {'plate': name}

        if isinstance(self.paths, str):
            return make_index(name, self.paths.format(name))

        if isinstance(self.paths, dict):
            if name not in self.paths:
                raise ConfigError(f"'{self.toml_path}' doesn't specify a path for plate '{name}'")
            return make_index(name, self.paths[name])

        raise ConfigError("{self.toml_path}: expected `meta.paths` to be dict or str, got {type(self.paths)}: {self.paths}")

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

class ConfigError(Exception):
    pass
