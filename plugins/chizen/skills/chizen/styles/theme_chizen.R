# CHI Zen theme for ggplot2: matches the pgfplots styles in CHIZen/figures.tex.
#
#   source("path/to/theme_chizen.R")
#   ggplot(d, aes(x, y, colour = group, linetype = group, shape = group)) +
#     geom_line() + geom_point() +
#     scale_colour_chizen() + theme_chizen()
#   ggsave("figures/model.pdf", width = 3.34, height = 2.36, units = "in")
#
# Needs ggplot2 3.4 or later (element_line(linewidth = ...)).
# See example_ggplot.R and the guide (references/figures.md).

library(ggplot2)

# Okabe-Ito colours in the order of the `chizen lines' cycle list (darkest first, no yellow).
chizen_palette <- c("#0072B2", "#D55E00", "#009E73", "#CC79A7", "#E69F00", "#56B4E9", "#000000")

# Sans-serif text at 8 pt, left and bottom axes only, a light horizontal grid, no tick marks
# on the x axis, and the legend centred below the plot without a frame or title.
theme_chizen <- function(base_size = 8, base_family = "sans") {
  theme_classic(base_size = base_size, base_family = base_family) %+replace%
    theme(
      axis.line = element_line(colour = "black", linewidth = 0.3),
      axis.ticks = element_line(colour = "black", linewidth = 0.3),
      axis.ticks.x = element_blank(),
      axis.text = element_text(colour = "black", size = rel(0.875)),
      panel.grid.major.y = element_line(colour = "grey85", linewidth = 0.3),
      legend.position = "bottom",
      legend.title = element_blank(),
      legend.background = element_blank(),
      legend.key = element_blank(),
      strip.background = element_blank(),
      strip.text = element_text(size = rel(1), margin = margin(2, 0, 2, 0)),
      plot.title.position = "plot"
    )
}

scale_colour_chizen <- function(...) scale_colour_manual(values = chizen_palette, ...)
scale_fill_chizen <- function(...) scale_fill_manual(values = chizen_palette, ...)
