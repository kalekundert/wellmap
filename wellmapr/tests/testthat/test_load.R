library(wellmapr)
context("wellmapr")
options("stringsAsFactors" = FALSE)

test_that("`load()` works on a simple layout", {
  layout <- wellmapr::load('toml/one_well_xy.toml')
  expected <- data.frame(well="A1",
                         well0="A01",
                         row="A",
                         col="1",
                         row_i=0,
                         col_j=0,
                         x=1,
                         y=1)

  expect_equivalent(!!layout, !!expected)
})

test_that("`read.csv()` is a valid `data_loader()`", {
  layout <- wellmapr::load(
                           'toml/one_well_xy.toml',
                           data_loader=read.csv,
                           merge_cols=TRUE,
                           path_guess="{0.stem}.csv")

  # Delete the path column.  It's an absolute path, so we don't really know 
  # what it should be.
  layout$path <- NULL

  expected <- data.frame(well="A1",
                         well0="A01",
                         row="A",
                         col="1",
                         row_i=0,
                         col_j=0,
                         x=1,
                         y=1,
                         Well="A1",
                         Data="xy")

  expect_equivalent(!!layout, !!expected)
})

test_that("`data_loader()` gets the `extras` argument", {
  data_loader <- function(toml_path, extras) {
    data_loader_extras <<- extras
    read.csv(toml_path)
  }
  layout <- wellmapr::load(
                           'toml/one_well_xy_extras.toml',
                           data_loader=data_loader,
                           merge_cols=TRUE,
                           extras="extras",
                           path_guess="{0.stem}.csv")
  layout[[1]]$path <- NULL

  expected <- data.frame(well="A1",
                         well0="A01",
                         row="A",
                         col="1",
                         row_i=0,
                         col_j=0,
                         x=1,
                         y=1,
                         Well="A1",
                         Data="xy")

  expect_equivalent(!!layout[[1]], !!expected)
  expect_equivalent(layout[[2]], list(a=1, b=1))
})

test_that("`on_alert()` path converted into string", {
  on_alert <- function(toml_path, message) {
    on_alert_path <<- toml_path
    on_alert_message <<- message
  }

  wellmapr::load('toml/one_well_xy_alert.toml', on_alert=on_alert)

  expected_path <- normalizePath(file.path(getwd(),
                                           "toml",
                                           "one_well_xy_alert.toml"))

  expect_equal(on_alert_path, expected_path)
  expect_equal(on_alert_message, "Hello world!")
})

test_that("`dependencies` reported as list of strings", {

  layout <- wellmapr::load('toml/one_well_xy.toml', report_dependencies=TRUE)
  expected_path <- normalizePath(file.path(getwd(),
                                           "toml",
                                           "one_well_xy.toml"))

  expect_equal(layout[[2]], expected_path)
})
