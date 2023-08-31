library(wellmapr)

test_that("`well_from_row_col()` is wrapped", {
  well <- wellmapr::well_from_row_col('A', '2')
  expect_equal(well, 'A2')
})

test_that("`well_from_ij()` is wrapped", {
  well <- wellmapr::well_from_ij(0L, 1L)
  expect_equal(well, 'A2')
})

test_that("`well0_from_well()` is wrapped", {
  well <- wellmapr::well0_from_well('A2')
  expect_equal(well, 'A02')

  well <- wellmapr::well0_from_well('A2', digits=3L)
  expect_equal(well, 'A002')
})

test_that("`well0_from_row_col()` is wrapped", {
  well <- wellmapr::well0_from_row_col('A', '2')
  expect_equal(well, 'A02')

  well <- wellmapr::well0_from_row_col('A', '2', digits=3L)
  expect_equal(well, 'A002')
})

test_that("`row_from_i()` is wrapped", {
  row <- wellmapr::row_from_i(0L)
  expect_equal(row, 'A')
})

test_that("`col_from_j()` is wrapped", {
  row <- wellmapr::col_from_j(0L)
  expect_equal(row, '1')
})

test_that("`row_col_from_ij()` is wrapped", {
  row_col <- wellmapr::row_col_from_ij(0L, 1L)
  expect_equal(row_col, list('A', '2'))
})

test_that("`row_col_from_well()` is wrapped", {
  row_col <- wellmapr::row_col_from_well('A2')
  expect_equal(row_col, list('A', '2'))
})

test_that("`i_from_row()` is wrapped", {
  i <- wellmapr::i_from_row('A')
  expect_equal(i, 0L)
})

test_that("`j_from_col()` is wrapped", {
  j <- wellmapr::j_from_col('1')
  expect_equal(j, 0L)
})

test_that("`ij_from_well()` is wrapped", {
  ij <- wellmapr::ij_from_well('A2')
  expect_equal(ij, list(0L, 1L))
})

test_that("`ij_from_row_col()` is wrapped", {
  ij <- wellmapr::ij_from_row_col('A', '2')
  expect_equal(ij, list(0L, 1L))
})

test_that("`iter_ij_in_block()` is wrapped", {
  indices <- wellmapr::iter_ij_in_block(list(0L, 1L), 2L, 2L)
  expected <- list(list(0L, 1L), list(0L, 2L), list(1L, 1L), list(1L, 2L))
  expect_equal(indices, expected)
})

test_that("`iter_row_indices()` is wrapped", {
  indices <- wellmapr::iter_row_indices('A')
  expect_equal(indices, c(0L))

  indices <- wellmapr::iter_row_indices('A,B')
  expect_equal(indices, c(0L, 1L))

  indices <- wellmapr::iter_row_indices('A-C')
  expect_equal(indices, c(0L, 1L, 2L))
})

test_that("`iter_col_indices()` is wrapped", {
  indices <- wellmapr::iter_col_indices('1')
  expect_equal(indices, c(0L))

  indices <- wellmapr::iter_col_indices('1,2')
  expect_equal(indices, c(0L, 1L))

  indices <- wellmapr::iter_col_indices('1-3')
  expect_equal(indices, c(0L, 1L, 2L))
})

test_that("`iter_well_indices()` is wrapped", {
  indices <- wellmapr::iter_well_indices('A1')
  expect_equal(indices, list(list(0L, 0L)))

  indices <- wellmapr::iter_well_indices('A1,B2')
  expect_equal(indices, list(list(0L, 0L), list(1L, 1L)))

  indices <- wellmapr::iter_well_indices('A1-B2')
  expected <- list(list(0L, 0L), list(0L, 1L), list(1L, 0L), list(1L, 1L))
  expect_equal(indices, expected)
})

