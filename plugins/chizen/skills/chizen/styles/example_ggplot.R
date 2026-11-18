# Tiny example of the CHI Zen ggplot2 theme.
#
#   Rscript example_ggplot.R     # writes example_ggplot.pdf in the current directory
#
# Two series over time, distinguishable in black and white (colour, line type and shape),
# with the legend centred below the plot. The numbers are made up for the example only.

args <- commandArgs(trailingOnly = FALSE)
here <- dirname(normalizePath(sub("^--file=", "", args[grep("^--file=", args)])))
source(file.path(here, "theme_chizen.R"))

d <- data.frame(
  month = rep(1:12, 2),
  count = c(150, 180, 210, 260, 300, 320, 360, 400, 430, 470, 520, 560,   # example values
            120, 130, 160, 170, 210, 230, 240, 280, 300, 310, 350, 380),  # example values
  series = rep(c("Distinct users", "Active threads"), each = 12)
)
d$series <- factor(d$series, levels = c("Distinct users", "Active threads"))

p <- ggplot(d, aes(month, count, colour = series, linetype = series, shape = series)) +
  geom_line(linewidth = 0.4) +
  geom_point(size = 1.2) +
  scale_colour_chizen() +
  scale_y_continuous(limits = c(0, NA), expand = expansion(mult = c(0, 0.05))) +
  labs(x = "Month", y = "Count per month") +
  theme_chizen()

ggsave("example_ggplot.pdf", p, width = 3.34, height = 2.36, units = "in")
cat("wrote example_ggplot.pdf\n")
