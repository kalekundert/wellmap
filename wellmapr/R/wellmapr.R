.onLoad <- function(libname, pkgname) {
  reticulate::configure_environment(pkgname)
}

#' Load a microplate layout from a TOML file.
#'
#' Parse the given TOML file and return a data frame with a row for each well 
#' and a column for each experimental condition specified in that file.  If the 
#' 'data_loader' and 'merge_cols' arguments are provided (which is the most 
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
#' Indicates that `load()` should attempt to merge the plate layout and the 
#' actual data associated with it into a single data frame.  This functionality 
#' requires several conditions to be met:
#' 
#' 1. The `data_loader` argument must be specified (otherwise there'd be no 
#'    data to merge).
#' 
#' 2. The data frame returned by `data_loader()` must be 
#'    [tidy](http://vita.had.co.nz/papers/tidy-data.html).
#'    Briefly, a data frame is tidy if each of its columns represents a single 
#'    variable (e.g. time, fluorescence) and each of its rows represents a 
#'    single observation.  
#' 
#' 3. The data frame returned by `data_loader()` must have one (or more) 
#'    columns/variables indicating which well each row/observation comes from.  
#'    For example, a column called "Well" with values like "A1", "A2", "B1", 
#'    "B2", etc. would satisfy this requirement.
#' 
#' The `merge_cols` argument specifies which columns to use when merging the 
#' data frames representing the layout and the actual data (i.e. the two data 
#' frames that would be returned if `data_loader` was specified but 
#' `merge_cols` was not) into one.  The argument can either be NULL, TRUE, or a 
#' named list:
#' 
#' If *NULL*, the data frames will be returned separately and not be merged.  
#' This is the default behavior.
#' 
#' If *TRUE*, the data frames will be merged using any columns that share the 
#' same name.  For example, the layout will always have a column named *well*, 
#' so if the actual data also has a column named *well*, the merge would happen 
#' on those columns.
#' 
#' If a named list, the keys and values identify the names of the columns that 
#' correspond with each other for the purpose of merging.  Each key should be 
#' one of the columns from the data frame representing the layout loaded from 
#' the TOML file.  This data frame has 8 columns which identify the wells: 
#' *plate*, *path*, *well*, *well0*, *row*, *col*, *row_i*, *row_j*.  See the 
#' "Returns" section below for more details on the differences between these 
#' columns.  Note that the *path* column is included in the merge automatically 
#' and never has to be specified.  Each value should be one of the columns from 
#' the data frame representing the actual data.  This data frame will have 
#' whatever columns were created by `data_loader()`.  
#' 
#' Note that the columns named in each key-value pair must contain values that 
#' correspond exactly (i.e. not "A1" and "A01").  It is the responsibility of 
#' `data_loader()` to ensure that this is possible.
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
#' @param extras
#' One or more keys to extract directly from the given TOML file.  Typically, 
#' this would be used to get information pertaining to the whole analysis and 
#' not any wells in particular (e.g. instruments used, preferred algorithms, 
#' plotting parameters, etc.).  Either one key (string) or multiple keys (list) 
#' can be specified.  [Dotted keys](https://github.com/toml-lang/toml#keys) are 
#' supported.  Specifying this argument causes the value(s) corresponding to 
#' the given key(s) to be returned, see below.
#' 
#' @param report_dependencies
#' If *TRUE*, return a vector of all the TOML files that were read in the 
#' process of loading the layout from the given `toml_path`.  See the 
#' description of `dependencies` below for more details.  You can use this 
#' information in analysis scripts (e.g. in conjunction with 
#' `file.info()$mtime`) to avoid repeating expensive analyses if the underlying 
#' layout hasn't changed.
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
#' If `extras` was provided:
#' 
#' - `extras`: The value(s) corresponding to the specified "extra" key(s).  If 
#'   only one extra key was specified, only that value will be returned.  If 
#'   multiple extra keys were specified, a named list containing the value for 
#'   each such key will be returned.  For example, consider the following TOML 
#'   file:
#' 
#'       a = 1
#'       b = 2
#' 
#'   If we were to load this file with `extras='a'`, this return value would 
#'   simply be `1`.  With `extras=['a', 'b']`, the same return value would 
#'   be `list(a=1, b=2)` instead.
#'
#' If `report_dependencies` was provided:
#'
#' - `dependencies`: A vector of absolute paths to every layout file that was 
#'   referenced by `toml_path`.  This includes `toml_path` itself, and the 
#'   paths to any 
#'   [included](https://wellmap.readthedocs.io/en/latest/file_format.html#meta-include) 
#'   or 
#'   [concatenated](https://wellmap.readthedocs.io/en/latest/file_format.html#meta-concat) 
#'   layout files.  It does not include paths to [data 
#'   files](https://wellmap.readthedocs.io/en/latest/file_format.html#meta-path), 
#'   as these are included already in the *path* column of the `layout` or 
#'   `merged` data frames.
#'
#' @import reticulate
#' @export

load <- function(toml_path, data_loader=NULL, merge_cols=NULL,
                 path_guess=NULL, path_required=FALSE, extras=NULL,
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
      wrapped_data_loader <- function(path, extras=NULL) {
        data_loader(reticulate::py_str(path), extras=extras)
      }
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
  wellmap <- reticulate::import("wellmap")

  retvals <- wellmap$load(
               toml_path=toml_path,
               data_loader=wrapped_data_loader,
               merge_cols=merge_cols,
               path_guess=path_guess, 
               path_required=path_required,
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
#' @param attrs
#' A list of attributes from the above TOML file to visualize.  For example, if 
#' the TOML file contains something equivalent to `well.A1.conc = 1`, then 
#' `conc` would be a valid attribute.  If no attributes are specified, the 
#' default is to display any attributes that have at least two different 
#' values. 
#' 
#' @param color
#' The name of the color scheme to use.  Each different value for each 
#' different attribute will be assigned a color from this scheme.  Any name 
#' understood by either [colorcet](http://colorcet.pyviz.org/) or 
#' [matplotlib](https://matplotlib.org/examples/color/colormaps_reference.html) 
#' can be used.
#'
#' @import reticulate
#' @export
show <- function(toml_path, attrs=NULL, color="rainbow") {
  wellmap <- reticulate::import("wellmap")
  fig <- wellmap$show(
               toml_path=toml_path,
               attrs=attrs,
               color=color)

  # Show the figure because R won't display it automatically.  
  plt <- reticulate::import("matplotlib.pyplot")
  plt$show()
}
