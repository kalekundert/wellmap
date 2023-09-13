wellmap <- NULL

.onLoad <- function(libname, pkgname) {
  reticulate::configure_environment(pkgname)
  wellmap <<- reticulate::import("wellmap", delay_load = TRUE)
}


#' Load a microplate layout from a TOML file.
#'
#' Parse the given TOML file and return a data frame with a row for each well 
#' and a column for each experimental condition specified in that file.  If the 
#' `data_loader` and `merge_cols` arguments are provided (which is the most 
#' typical use-case), that data frame will also contain columns for any data 
#' associated with each well.
#'
#' @param toml_path
#' The path to a file describing the layout of one or more plates.  See the 
#' [file format 
#' documentation](https://wellmap.readthedocs.io/en/latest/file_format.html) 
#' for details about this file.
#'
#' @param data_loader
#' Indicates that `load()` should attempt to load the actual data associated 
#' with the plate layout, in addition to loading the layout itself.  The 
#' argument should be a function that takes a path to a data file (string), 
#' parses it, and returns a data frame containing the parsed data.  The 
#' function may also take an argument named "extras", in which case the 
#' `extras` return value (described below) will be provided.  Note that 
#' specifying a data loader implies that `path_required` is True.
#'
#' @param merge_cols
#' Indicates whether or not---and if so, how---`load()` should merge the data 
#' frames representing the plate layout and the actual data (provided by 
#' `data_loader`).  The argument can either be `NULL`, `TRUE`, or a named list:
#'
#' If `NULL`, the data frames will be returned separately and not be merged.  
#' This is the default behavior.
#'
#' If `TRUE`, the data frames will be merged using any columns that share the 
#' same name.  For example, the layout will always have a column named *well*, 
#' so if the actual data also has a column named *well*, the merge would happen 
#' on those columns.
#'
#' If a named list, If a named list, the data frames will be merged using the 
#' columns identified in each key-value pair of the list.  The keys should be 
#' column names from the data frame representing the plate layout (described 
#' below; see the `layout` return value), and the values should be column names 
#' from the data frame returned by `data_loader`.  Below are some examples of 
#' this argument:
#'
#' - `list(well0 = 'Well')`: Indicates that the "Well" column in the data 
#'   contains zero-padded well names, like "A01", "A02", etc.
#'
#' - `list(row_i = 'Row', col_j = 'Col')`: Indicates that the 'Row' and 'Col' 
#'   columns in the data contain 0-indexed coordinates (e.g. 0, 1, 2, ...) 
#'   identifying each row and column, respectively.
#'
#' Some details and caveats:
#'
#' - In order to successfully merge two columns, the values in those columns 
#'   must correspond exactly.  For example, a column that contains unpadded 
#'   well names like "A1" cannot be merged with a column that contains padded 
#'   well names like "A01".  This is why the `layout` data frame contains so 
#'   many redundant columns: to increase the chance that one will correspond 
#'   exactly with a column provided by the data.  In some cases, though, it may 
#'   be necessary for the `data_loader` function to construct an appropriate 
#'   merge column.
#'
#' - The data frame returned by `data_loader()` must be 
#'   [tidy](http://vita.had.co.nz/papers/tidy-data.html).  Briefly, a data 
#'   frame is tidy if each of its columns represents a single variable (e.g.  
#'   time, fluorescence) and each of its rows represents a single observation.
#'    
#' - The *path* column of the layout is automatically included in the merge and 
#'   never has to be specified (although it is not an error to do so).  The 
#'   reason for this special-case is that `load()` itself knows what path each 
#'   data frame was loaded from.
#' 
#' @param path_guess
#' Where to look for a data file if none is specified in the given TOML file.  
#' In other words, this is the default value for 
#' [meta.path](https://wellmap.readthedocs.io/en/latest/file_format.html#meta-path).  
#' This path is interpreted relative to the TOML file itself (unless it's an 
#' absolute path) and is formatted in python with a `pathlib.Path` object 
#' representing said TOML file.  In code, that would be: 
#' `path_guess.format(Path(toml_path))`.  A typical value would be something 
#' like `'{0.stem}.csv'`.
#' 
#' @param path_required
#' Indicates whether or not the given TOML file must reference one or more data 
#' files.  It is an error if this condition is not met.  Data files found via 
#' `path_guess` are acceptable for this purpose.
#'
#' @param meta
#' If `TRUE`, return a 
#' [`Meta`](https://wellmap.readthedocs.io/en/latest/api/wellmap.Meta.html) 
#' object containing miscellaneous information that was read from the TOML file 
#' but not part of the layout.  This includes (i) a dictionary with all the 
#' key/values pairs present in the TOML file but not part of the layout, (ii) a 
#' set of all the TOML files that were read in the process of loading the 
#' layout from the given `toml_path`, (iii) and a [Style] object describing how 
#' to plot the layout itself.
#' 
#' @param extras
#' [Deprecated](https://wellmap.readthedocs.io/en/latest/deprecations.html#the-extras-and-report-dependencies-arguments-to-wellmap-load).
#' 
#' @param report_dependencies
#' [Deprecated](https://wellmap.readthedocs.io/en/latest/deprecations.html#the-extras-and-report-dependencies-arguments-to-wellmap-load).
#'
#' @param on_alert
#' A callback to invoke if the given TOML file contains a warning for the user.  
#' The default behavior is to print the warning to the terminal.  If a callback 
#' is provided, it must take two arguments: the path to to the TOML file 
#' containing the alert (string), and the message itself (string).  Note that 
#' this could be called more than once, e.g. if there are included or 
#' concatenated files.
#' 
#' @return
#' If neither `data_loader` nor `merge_cols` were provided:
#'
#' - `layout` (data frame): Information about the plate layout parsed from the 
#'   given TOML file.  The data frame will have a row for each well and a 
#'   column for each experimental condition.  In addition, there will be 
#'   several columns identifying each well:
#' 
#'   - *plate*: The name of the plate for this well.  This column will not be 
#'     present if there are no `[plate]` blocks in the TOML file.
#'   - *path*: The path to the data file associated with the plate for this 
#'     well.  This column will not be present if no data files were referenced 
#'     by the TOML file.
#'   - *well*: The name of the well, e.g. "A1".
#'   - *well0*: The zero-padded name of the well, e.g. "A01".
#'   - *row*: The name of the row for this well, e.g. "A".
#'   - *col*: The name of the column for this well, e.g. "1".
#'   - *row_i*: The row-index of this well, counting from 0.
#'   - *col_j*: The column-index of this well, counting from 0.
#' 
#' If `data_loader` was provided but `merge_cols` was not:
#' 
#' - `layout` (data frame): See above.
#' 
#' - `data` (data frame): The concatenated result of calling `data_loader()` on 
#'   every path specified in the given TOML file.  See 
#'   [`pandas.concat()`](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.concat.html) 
#'   for more information on how the data from different paths are 
#'   concatenated.
#' 
#' If `data_loader` and `merge_cols` were both provided:
#' 
#' - `merged` (data frame): The result of merging the `layout` and `data` data 
#'   frames along the columns specified by `merge_cols`.  See 
#'   [`pandas.merge()`](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.merge.html) 
#'   for more details on the merge itself.  The resulting data frame will have 
#'   one or more rows for each well (more are possible if there are multiple 
#'   data points per well, e.g. a time course), a column for each experimental 
#'   condition described in the TOML file, and a column for each kind of data 
#'   loaded from the data files.  
#'   
#' If `meta` was requested:
#' 
#' - `meta`: As described above.
#'
#' @export
load <- function(toml_path, data_loader=NULL, merge_cols=NULL,
                 path_guess=NULL, path_required=FALSE, meta=NULL, extras=NULL,
                 report_dependencies=FALSE, on_alert=NULL) {

  # The 'data_loader' argument requires a little bit of manipulation:
  #
  # - The python code will pass a `pathlib.Path` object as the first argument 
  #   to this callback.  Of course, nothing in R will know what to do with 
  #   this, so we convert it into a string.
  #
  # - The python code will inspect the arguments of the callback to decide 
  #   whether or not to provide the 'extras' argument.  In order to expose this 
  #   information to python, we need to convert the wrapper function to a 
  #   python object using py_func().  We also need to make sure the wrapper 
  #   function has an 'extras' argument if the given callback does.

  if (is.null(data_loader)) {
    wrapped_data_loader <- NULL
  } else {
    have_extras <- "extras" %in% names(formals(data_loader))
    if (have_extras) {
      wrapped_data_loader_with_extras <- function(path, extras=NULL) {
        data_loader(reticulate::py_str(path), extras=extras)
      }
      wrapped_data_loader <- wrapped_data_loader_with_extras
    } else {
      wrapped_data_loader <- function(path) {
        data_loader(reticulate::py_str(path))
      }
    }

    wrapped_data_loader <- reticulate::py_func(wrapped_data_loader)
  }

  # Similar to above, the `on_alert` argument also needs to convert a 
  # `pathlib.Path` into a string.

  if (is.null(on_alert)) {
    wrapped_on_alert <- NULL
  } else {
    wrapped_on_alert <- function(path, message) {
      on_alert(reticulate::py_str(path), message)
    }
  }

  # Call 'wellmap.load()':

  builtins <- reticulate::import("builtins")

  retvals <- wellmap$load(
               toml_path=toml_path,
               data_loader=wrapped_data_loader,
               merge_cols=merge_cols,
               path_guess=path_guess, 
               path_required=path_required,
               meta=meta,
               extras=extras,
               report_dependencies=report_dependencies,
               on_alert=wrapped_on_alert)

  if (report_dependencies) {
    n <- length(retvals)
    retvals[[n]] <- sapply(builtins$list(retvals[[n]]), reticulate::py_str)
  }

  retvals
}


#' Visualize the given microplate layout.
#'
#' It's wise to visualize TOML layouts before doing any analysis, to ensure 
#' that all of the wells are correctly annotated.  The `wellmap` command-line 
#' program is a useful tool for doing this, but sometimes it's more convenient 
#' to make visualizations directly from R/Rstudio.  That's what this function 
#' is for.
#' 
#' @param toml_path
#' The path to a file describing the layout of one or more plates.  See the 
#' [file format 
#' documentation](https://wellmap.readthedocs.io/en/latest/file_format.html) 
#' for details about this file.
#' 
#' @param params
#' The names of one or more experimental parameters from the above TOML file to 
#' visualize.  For example, if the TOML file contains something equivalent to 
#' `well.A1.conc = 1`, then `"conc"` would be a valid parameter name.  If not 
#' specified, the default is to display any parameters that have at least two 
#' different values. 
#' 
#' @param style
#' Settings that control miscellaneous aspects of the plot, e.g. colors, 
#' dimensions, etc.  See [Style] for more info.
#'
#' @export
show <- function(toml_path, params=NULL, style=NULL) {
  fig <- wellmap$show(
               toml_path=toml_path,
               params=params,
               style=style)

  # RStudio hooks into `plt.show()` to render plots made in python, so we need 
  # to make sure it gets called.
  plt <- reticulate::import("matplotlib.pyplot")
  plt$show()
}


#' Visualize the microplate layout described by the given data frame.
#' 
#' @description
#' Unlike the [show()] function and the `wellmap` command-line program, this 
#' function is not limited to displaying layouts parsed directly from TOML 
#' files.  Any data frame that specifies a well for each row can be plotted.  
#' This provides the means to:
#' 
#' - Project experimental data onto a layout.
#' - Visualize layouts that weren't generated by wellmap in the first place.
#' 
#' For example, you could load experimental data into a data frame and use 
#' this function to visualize it directly, without ever having to specify a 
#' layout.  This might be a useful way to get a quick sense for the data.
#' 
#' @param df
#' The data frame describing the layout to plot.  The data frame must be 
#' [tidy](http://vita.had.co.nz/papers/tidy-data.html): each row must describe 
#' a single well, and each column must describe a single aspect of each well.  
#' The location of each well must be specified using one or more of the same 
#' columns that wellmap uses for that purpose, namely:
#' 
#' - `plate`
#' - `path`
#' - `well`
#' - `well0`
#' - `row`
#' - `col`
#' - `row_i`
#' - `col_j`
#' 
#' See [load()] for the exact meanings of these columns.  It's not necessary to 
#' specify all of these columns, there just needs to be enough information to 
#' locate each well.  If the *plate* column is missing, it is assumed that all 
#' of the wells are on the same plate.  It is also assumed that any redundant 
#' columns (e.g. *row* and *row_i*) will be consistent with each other.
#' 
#' Any scalar-valued columns other than these can be plotted.
#' 
#' @param cols
#' Which columns to plot onto the layout.  The columns used to locate the 
#' wells (listed above) cannot be plotted.  The default is to include any 
#' columns that have at least two different values.
#' 
#' @param style
#' Settings than control miscellaneous aspects of the plot, e.g. colors, 
#' dimensions, etc.  See [Style] for more info.
#' 
#' @export
show_df <- function(df, cols=NULL, style=NULL) {
  fig <- wellmap$show_df(
               df=df,
               cols=cols,
               style=style)

  # RStudio hooks into `plt.show()` to render plots made in python, so we need 
  # to make sure it gets called.
  plt <- reticulate::import("matplotlib.pyplot")
  plt$show()
}


#' Describe how to plot well layouts.
#'
#' Style objects exist to be passed to [show()] or [show_df()], where they 
#' determine various aspects of the plots' appearances.  The following 
#' parameters can be specified:
#'
#' @param .kw_only
#' This just exists to check that all the other arguments are named, and not 
#' just specified positionally.  The order of these arguments is not guaranteed 
#' to remain the same in different versions of wellmap.
#' 
#' @param cell_size
#' The size of the boxes representing each well, in inches.  The default is 
#' 0.25".
#'
#' @param pad_width
#' The vertical padding between layouts, in inches.  The default is 0.2".
#'
#' @param pad_height
#' The horizontal padding between layouts, in inches.  The default is 0.2".
#' 
#' @param bar_width
#' The width of the color bar, in inches.  The default is 0.15".
#' 
#' @param bar_pad_width
#' The horizontal padding between the color bar and the nearest layout, in 
#' inches.  The default is 0.2".
#' 
#' @param top_margin
#' The space between the layouts and the top edge of the figure, in inches.  
#' The default is 0.5".
#' 
#' @param left_margin
#' The space between the layouts and the left edge of the figure, in inches.  
#' The default is 0.5".
#' 
#' @param right_margin
#' The space between the layouts and the right edge of the figure, in inches.  
#' The default is 0.2".
#' 
#' @param bottom_margin
#' The space between the layouts and the bottom edge of the figure, in inches.  
#' The default is 0.2".
#' 
#' @param color_scheme
#' The name of the color scheme to use.  Each different value for each
#' different parameter will be assigned a color from this scheme.  Any name
#' understood by either [colorcet](http://colorcet.pyviz.org/) or
#' [matplotlib](https://matplotlib.org/examples/color/colormaps_reference.html)
#' can be used.
#'
#' @export
Style <- function(.kw_only=NULL, cell_size=0.25, pad_width=0.20, pad_height=0.20, bar_width=0.15, bar_pad_width=0.20, top_margin=0.5, left_margin=0.5, right_margin=0.20, bottom_margin=0.20, color_scheme='rainbow') {
  if (! is.null(.kw_only)) {
    stop("When constructing style objects, use keyword arguments instead of positional arguments.  The order of the arguments is not guaranteed and may change in any minor version of wellmap!")
  }

  wellmap$Style(
               cell_size=cell_size,
               pad_width=pad_width,
               pad_height=pad_height,
               bar_width=bar_width,
               bar_pad_width=bar_pad_width,
               top_margin=top_margin,
               left_margin=left_margin,
               right_margin=right_margin,
               bottom_margin=bottom_margin,
               color_scheme=color_scheme)
}


#' Create a well name from the given row and column names.
#'
#' @param row Row name
#' @param col Column name
#'
#' @examples
#' well_from_row_col('A', '2')  # returns 'A2'
#' 
#' @seealso
#' [Well Formats](https://wellmap.readthedocs.io/en/latest/well_formats.html) 
#'
#' @export
well_from_row_col <- function(row, col) {
  wellmap$well_from_row_col(row, col)
}


#' Create a well name from the given row and column indices.
#' 
#' @param i
#' Row index
#'
#' @param j
#' Column index
#'
#' @details
#' The given indices must be integers, i.e. `0L` instead of `0`.
#' 
#' @examples
#' well_from_ij(0L, 1L)  # returns 'A2'
#'
#' @seealso
#' [Well Formats](https://wellmap.readthedocs.io/en/latest/well_formats.html) 
#'
#' @export
well_from_ij <- function(i, j) {
  wellmap$well_from_ij(i, j)
}


#' Create a zero-padded well name from the given well name.
#' 
#' @param well Well name
#' @param digits Minimum number of digits for column names.
#'
#' @details
#' - It doesn't matter if the input name is zero-padded or not.
#' - If specified, the number of column digits must be an integer, i.e. `2L` 
#'   instead of `2`.
#' 
#' @examples
#' well0_from_well('A2')  # returns 'A02'
#' 
#' @seealso
#' [Well Formats](https://wellmap.readthedocs.io/en/latest/well_formats.html) 
#'
#' @export
well0_from_well <- function(well, digits=2L) {
  wellmap$well0_from_well(well, digits)
}


#' Create a zero-padded well name from the given row and column names.
#'
#' @param row Row name
#' @param col Column name
#' @param digits Minimum number of digits for column names.
#'
#' @details
#' If specified, the number of column digits must be an integer, i.e. `2L` 
#' instead of `2`.
#'
#' @examples
#' well0_from_row_col('A', '2')  # returns 'A02'
#'
#' @seealso
#' [Well Formats](https://wellmap.readthedocs.io/en/latest/well_formats.html) 
#'
#' @export
well0_from_row_col <- function(row, col, digits=2L) {
  wellmap$well0_from_row_col(row, col, digits)
}


#' Convert the given index into a row name.
#'
#' @param i Row index
#'
#' @details
#' - The given row index must be an integer, i.e. `0L` instead of `0`.
#' - The row after 'Z' is 'AA'.
#'
#' @examples
#' row_from_i(0L)  # returns 'A'
#'
#' @seealso
#' [Well Formats](https://wellmap.readthedocs.io/en/latest/well_formats.html) 
#'
#' @export
row_from_i <- function(i) {
  wellmap$row_from_i(i)
}


#' Convert the given index into a column name.
#'
#' @param j Column index
#'
#' @details
#' - The given column index must be an integer, i.e. `0L` instead of `0`.
#' - Column names count from 1, and are strings.
#'
#' @examples
#' col_from_j(0L)  # returns '1'
#'
#' @seealso
#' [Well Formats](https://wellmap.readthedocs.io/en/latest/well_formats.html) 
#'
#' @export
col_from_j <- function(j) {
  wellmap$col_from_j(j)
}


#' Convert the given indices into row and column names.
#'
#' @param i Row index
#' @param j Column index
#'
#' @details
#' The given indices must be integers, i.e. `0L` instead of `0`.
#'
#' @examples
#' row_col_from_ij(0L, 1L)  # returns list('A', '2')
#'
#' @seealso
#' [Well Formats](https://wellmap.readthedocs.io/en/latest/well_formats.html) 
#'
#' @export
row_col_from_ij <- function(i, j) {
  wellmap$row_col_from_ij(i, j)
}


#' Split row and column names out of the given well name.
#'
#' @param well Well name
#'
#' @details
#' The well name is allowed to be zero-padded.
#'
#' @examples
#' row_col_from_well('A2')  # returns list('A', '2')
#'
#' @seealso
#' [Well Formats](https://wellmap.readthedocs.io/en/latest/well_formats.html) 
#'
#' @export
row_col_from_well <- function(well) {
  wellmap$row_col_from_well(well)
}


#' Convert the given row name into an index number.
#'
#' @param row Row name
#'
#' @examples
#' i_from_row('A')  # returns 0L
#'
#' @seealso
#' [Well Formats](https://wellmap.readthedocs.io/en/latest/well_formats.html) 
#'
#' @export
i_from_row <- function(row) {
  wellmap$i_from_row(row)
}


#' Convert the given column name into an index number.
#'
#' @param col Column name
#'
#' @details
#' Note that column names count from 1.
#'
#' @examples
#' j_from_col('1')  # returns 0L
#'
#' @seealso
#' [Well Formats](https://wellmap.readthedocs.io/en/latest/well_formats.html) 
#'
#' @export
j_from_col <- function(col) {
  wellmap$j_from_col(col)
}


#' Convert the given well name into row and column indices.
#'
#' @param well Well name
#'
#' @examples
#' ij_from_well('A2')  # returns list(0L, 1L)
#'
#' @seealso
#' [Well Formats](https://wellmap.readthedocs.io/en/latest/well_formats.html) 
#'
#' @export
ij_from_well <- function(well) {
  wellmap$ij_from_well(well)
}


#' Convert the given row and column names into indices.
#'
#' @param row Row name
#' @param col Column name
#'
#' @examples
#' ij_from_row_col('A', '2')  # returns list(0L, 1L)
#'
#' @seealso
#' [Well Formats](https://wellmap.readthedocs.io/en/latest/well_formats.html) 
#'
#' @export
ij_from_row_col <- function(row, col) {
  wellmap$ij_from_row_col(row, col)
}


#' Find all of the well indices in the given block.
#'
#' @param top_left_ij Row/column indices for the top-left corner of the block.
#' @param width The number of columns spanned by the block.
#' @param height The number of rows spanned by the block.
#'
#' @details
#' - The given indices and dimensions must be integers, i.e. `1L` instead of 
#'   `1`.
#'
#' @examples
#' iter_ij_in_block(list(0L, 1L), 2L, 2L)
#'
#' @seealso
#' [Well Formats](https://wellmap.readthedocs.io/en/latest/well_formats.html) 
#'
#' @export
iter_ij_in_block <- function(top_left_ij, width, height) {
  builtins <- reticulate::import_builtins()
  indices <- wellmap$iter_ij_in_block(top_left_ij, width, height)
  builtins$list(indices)
}


#' Yield all of the well indices in the given row(s).
#'
#' @param pattern A string identifying either a single row (e.g. "A") or 
#' several, using the pattern syntax (e.g. "A,B", "A-C", "A,C,...,G").
#'
#' @examples
#' iter_row_indices('A')  # returns c(0L)
#' iter_row_indices('A,B')  # returns c(0, 1)
#' iter_row_indices('A-C')  # returns c(0, 1, 2)
#'
#' @seealso
#' [Well Formats](https://wellmap.readthedocs.io/en/latest/well_formats.html) 
#'
#' @export
iter_row_indices <- function(pattern) {
  builtins <- reticulate::import_builtins()
  indices <- wellmap$iter_row_indices(pattern)
  builtins$list(indices)
}


#' Yield all of the well indices in the given column(s).
#'
#' @param pattern A string identifying either a single column (e.g. "1") or 
#' several, using the pattern syntax (e.g. "1,2", "1-3", "1,3,...,11").
#'
#' @examples
#' iter_col_indices('1')  # returns c(0L)
#' iter_col_indices('1,2')  # returns c(0L, 1L)
#' iter_col_indices('1-3')  # returns c(0L, 1L, 2L)
#'
#' @seealso
#' [Well Formats](https://wellmap.readthedocs.io/en/latest/well_formats.html) 
#'
#' @export
iter_col_indices <- function(pattern) {
  builtins <- reticulate::import_builtins()
  indices <- wellmap$iter_col_indices(pattern)
  builtins$list(indices)
}


#' Yield the indices for the given well(s).
#' 
#' @param pattern A string identifying either a single well (e.g. "A1") or 
#' several, using the pattern syntax (e.g. "A1,B2", "A1-B2", "A1,A3,...,B11").
#'
#' @examples
#' iter_well_indices('A1')  # returns list(list(0L, 0L))
#' iter_well_indices('A1,B2')  # returns list(list(0L, 0L), list(1L, 1L))
#' iter_well_indices('A1-B2')  # returns list(list(0L, 0L), list(0L, 1L), list(1L, 0L), list(1L, 1L))
#'
#' @seealso
#' [Well Formats](https://wellmap.readthedocs.io/en/latest/well_formats.html) 
#'
#' @export
iter_well_indices <- function(pattern) {
  builtins <- reticulate::import_builtins()
  indices <- wellmap$iter_well_indices(pattern)
  builtins$list(indices)
}

