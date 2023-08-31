library(wellmapr)

# I test the `show()` and `show_df()` wrappers interactively, because the 
# outputs of those functions are fundamentally visual and interactive.  Here, I 
# just test auxiliary tools, like the style object.

test_that("all of the style arguments work", {
  style <- wellmapr::Style(
               cell_size=1,
               pad_width=2,
               pad_height=3,
               bar_width=4,
               bar_pad_width=5,
               top_margin=6,
               left_margin=7,
               right_margin=8,
               bottom_margin=9,
               color_scheme="a")

  expect_equal(style$cell_size, 1)
  expect_equal(style$pad_width, 2)
  expect_equal(style$pad_height, 3)
  expect_equal(style$bar_width, 4)
  expect_equal(style$bar_pad_width, 5)
  expect_equal(style$top_margin, 6)
  expect_equal(style$left_margin, 7)
  expect_equal(style$right_margin, 8)
  expect_equal(style$bottom_margin, 9)
  expect_equal(style$color_scheme, "a")
})

test_that("positional arguments aren't allowed", {
  expect_error(wellmapr::Style(1))
})
