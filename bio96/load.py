#!/usr/bin/env python3

import toml
import itertools
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

def load(toml_path, path_guess=None):
    config, paths = config_from_toml(toml_path, path_guess)
    return table_from_config(config, paths)

def config_from_toml(toml_path, path_guess=None):
    toml_path = Path(toml_path).resolve()
    config = configdict(toml.load(str(toml_path)))

    # Synthesize any available path information.
    paths = PathManager(
            config.meta.get('path'),
            config.meta.get('paths'),
            toml_path,
            path_guess,
    )

    # Include one or more remote files if any are specified.  
    if 'include' in config.meta:
        includes = config.meta['include']
        if isinstance(includes, str):
            includes = list(includes)

        for include_path in reversed(includes):
            defaults, _ = config_from_toml(include_path)
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

        return pd.concat(tables)

def wells_from_config(config, label=None):
    config = configdict(config)
    wells = config.wells.copy()

    # Create new wells implied by the 'row' and 'col' blocks.
    for row, col in itertools.product(config.rows, config.cols):
        key = well_from_row_col(row, col)
        wells.setdefault(key, {})

    for irow, col in itertools.product(config.irows, config.cols):
        key = well_from_irow_col(irow, col)
        wells.setdefault(key, {})

    for row, icol in itertools.product(config.rows, config.icols):
        key = well_from_row_icol(row, icol)
        wells.setdefault(key, {})
    
    # Update any existing wells.
    for key in wells:
        row, col = row_col_from_well(key)
        irow, icol = irow_icol_from_well(key)

        recursive_merge(wells[key], config.user)
        recursive_merge(wells[key], config.rows.get(row, {}))
        recursive_merge(wells[key], config.cols.get(col, {}))
        recursive_merge(wells[key], config.irows.get(irow, {}))
        recursive_merge(wells[key], config.icols.get(icol, {}))

    return wells
    
def table_from_wells(wells, index):
    table = []

    for key in wells:
        row, col = row_col_from_well(key)
        row_i, col_j = ij_from_well(key)

        table += [{
                **wells[key],
                **index,
                'well': key,
                'row': row, 'col': col,
                'row_i': row_i, 'col_j': col_j,
        }]

    return pd.DataFrame(table)


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

class PathManager:

    def __init__(self, path, paths, toml_path, path_guess=None):
        self.path = path
        self.paths = paths
        self.toml_path = Path(toml_path)
        self.path_guess = path_guess

    def __str__(self):
        return str({
            'path': self.path,
            'paths': self.paths,
            'toml_path': self.toml_path,
            'path_guess': self.path_guess,
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
            path = Path(path)
            if not path.is_absolute():
                path = self.toml_path.parent / path
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
            path = Path(path)
            if not path.is_absolute():
                path = self.toml_path.parent / path
            if not path.exists:
                raise ConfigError(f"'{path}' for plate '{name}' does not exist")
            return {'plate': name, 'path': path}

        if self.paths is None:
            return {'plate': name}

        if isinstance(self.paths, str):
            return make_index(name, self.paths.format(name))

        if isinstance(self.paths, dict):
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
