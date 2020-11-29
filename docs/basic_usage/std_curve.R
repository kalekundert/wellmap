library(tidyverse)

load_cq <- function(path) {
  read_csv(path) %>%
  rename(row = Cq) %>%
  pivot_longer(
      !row,
      names_to = "col",
      values_to = "Cq",
  )
}
        
df <- wellmapr::load(
    "std_curve.toml",
    data_loader = load_cq,
    merge_cols = TRUE,
    path_guess = "{0.stem}.csv",
)

ggplot(df, aes(x = dilution, y = Cq)) +
  geom_point() +
  geom_smooth(method = "lm") +
  scale_x_log10()



